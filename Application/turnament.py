"""turnament.py

Turnament class with edit, run and summary.
Additional class with Player's data.

"""

# Global package imports:
from datetime import date
import logging
from pydantic import ValidationError

# Local package imports:
from Organization import Player, Round
from Organization.table import Table
from Systems import get_system
from Resources import SystemType, SystemNames
from Application.sql_utils import SqlUtils


class Turnament(object):
    def __init__(self, name, engine) -> None:
        # General:
        self._name = name
        self._date_start = date.today()
        self._date_end = None
        self._finished = False
        self._players_num = 0
        self._mean_rank = 0
        self._mean_age = 0
        self._rounds_num = 0
        self._act_round_nr = 0
        self._finished_round_nr = 0
        self._place = ""
        self.fine_to_begin = False
        self._system = SystemType.UNKNOWN
        self._players = []
        self._rounds = []
        self.sql = SqlUtils(engine)

        # Additional:
        self._place = ""

        # Post init:
        self.initialize_data_from_db()

    def initialize_data_from_db(self):
        """Read existing data from DB"""
        # @ToDo: Divide into methods
        # Initialize turnament table data:
        self.sql.turnament_init()
        self.sql.update_turnament_info(
            name=self._name, date_start=self._date_start, system=self._system
        )
        info = self.sql.read_turnament_info()[0]
        self._rounds_num = info.get("rounds") if info.get("rounds") else 0
        self._date_start = info.get("datestart")
        self._date_end = info.get("dateend")
        self._act_round_nr = info.get("roundactual") if info.get("roundactual") else 0
        self._finished_round_nr = (
            info.get("roundfinished") if info.get("roundfinished") else 0
        )
        self._place = info.get("place")
        self._system = info.get("system") if info.get("system") else SystemType.UNKNOWN
        self._finished = info.get("finished") if info.get("finished") else False
        # Initialize Players data from db:
        players = self.sql.read_players_info()
        players.sort(key=lambda x: x.get("nr") if x.get("nr") else 0, reverse=False)
        for player in players:
            self.add_player(
                _id=player.get("nr"),
                name=player.get("name"),
                surname=player.get("surname"),
                sex=player.get("sex", "male"),
                city=player.get("city", ""),
                category=player.get("category", "wc"),
                elo=player.get("elo", 0),
                insert_to_db=False,
            )
        # Initialize results of Rounds from db:
        self.load_results()

    @property
    def players_num(self):
        self._players_num = len(self._players)
        return self._players_num

    def set_system(self, system_id: int):
        if self._act_round_nr == 0:
            msg_info = f"Set {SystemNames[system_id]} round pairing system."
            logging.info(msg=msg_info)
            self._system = system_id
            self.sql.update_turnament_info(system=self._system)

    def set_start_date(self, start):
        self._date_start = start
        self.sql.update_turnament_info(date_start=self._date_start)

    def set_end_date(self, end):
        self._date_end = end
        self.sql.update_turnament_info(date_end=self._date_end)

    def add_player(
        self,
        name="",
        surname="",
        sex="male",
        city="",
        category="wc",
        elo=0,
        _id=None,
        insert_to_db=True,
    ):
        def _player_already_exists(name, surname):
            # Validate Player add:
            for player in self._players:
                if player.name == name and player.surname == surname:
                    msg_error_1 = (
                        f"\nPlayer {name} {surname} already set into turnament."
                    )
                    logging.error(msg=msg_error_1)
                    return True
            return False

        # Add Player:
        if not _player_already_exists(name, surname):
            try:
                player = Player(
                    name=name,
                    surname=surname,
                    sex=sex or "male",
                    city=city,
                    category=str(category),
                    elo=elo,
                )
            except ValidationError as exc:
                msg_error_2 = f"\nCannot add Player {name} {surname} with invalid data."
                logging.error(msg=str(exc) + msg_error_2)
            else:
                # Assign player ID
                if _id:
                    player.id = _id
                elif self._act_round_nr > 0:
                    # Tournament is active (in a round) - assign next available ID
                    max_id = max([p.id for p in self._players if p.id > 0], default=0)
                    player.id = max_id + 1
                # else: player.id remains 0 (will be assigned when begin() is called)

                # If tournament is active, suspend the player for the current round
                # They will participate starting from the next round
                if self._act_round_nr > 0 and self.fine_to_begin:
                    player.suspend_player(self._act_round_nr)
                    msg_info = (
                        f"Player {player.name} {player.surname} suspended for "
                        f"round {self._act_round_nr}, will play from round {self._act_round_nr + 1}."
                    )
                    logging.info(msg=msg_info)

                self._players.append(player)
                if insert_to_db:
                    self.sql.insert_player_info(
                        name=name,
                        surname=surname,
                        sex=sex,
                        city=city,
                        category=category,
                        elo=elo,
                    )
                    # If player has an assigned ID (mid-tournament add), save it to DB
                    if player.id > 0:
                        self.sql.update_player_info(
                            name=name, surname=surname, nr=player.id
                        )
                msg_info = (
                    f"Set Player: {player.name} {player.surname}, "
                    + f"[elo: {player.elo}, cat: {player.category}] into turnament."
                )
                logging.info(msg=msg_info)

    def del_player(self, name="", surname=""):
        list_index = 0
        for player in self._players:
            if player.exist(name=name, surname=surname):
                msg_info = (
                    f"Remove: {player.name} " + f"{player.surname} from turnament."
                )
                logging.info(msg=msg_info)
                self._players.pop(list_index)
                self.sql.remove_player_info(name=name, surname=surname)
                logging.debug(f"Last players: {self._players}")
                return True
            list_index += 1
        msg_info = f"No Player #{player.id} on turnament list."
        logging.error(msg=msg_info)
        return False

    def add_result(self, table_nr, result):
        round_id = self._act_round_nr - 1
        if self.fine_to_begin:
            step = 1
            try:
                self._rounds[round_id].set_result(table_nr, result)
                step += 1
                logging.debug(f"self._rounds={self._rounds}")
                player_w = self._rounds[round_id].tables[table_nr].w_player.id
                player_b = self._rounds[round_id].tables[table_nr].b_player.id
                step += 1
                self.sql.insert_result(
                    round=self._act_round_nr,
                    table=table_nr,
                    player_w=player_w,
                    player_b=player_b,
                    result=result,
                )
            except KeyError as exc:
                msg_error = f"Used values: round_id={round_id}, table_nr={table_nr}. (step={step}; \n {exc})"
                logging.error(msg=msg_error)
        else:
            msg_error = f"Something is wrong, turnament did not start. System {SystemNames[self._system]}."
            logging.error(msg=msg_error)

    def begin(self, rounds):
        if isinstance(rounds, int):
            if self._system == SystemType.UNKNOWN:
                msg_error = "Please set pairing system for turnament."
                logging.error(msg=msg_error)
            elif 0 < rounds < 23 and self.players_num > 1:
                self.fine_to_begin = True
                self._begin(rounds)
                self.set_start_date(date.today())
            else:
                msg_error = "Please add more Players to the event."
                logging.error(msg=msg_error)

    def _begin(self, rounds):
        self._rounds_num = rounds
        self._act_round_nr = 1
        self.sql.update_turnament_info(rounds=rounds, roundactual=self._act_round_nr)
        self._players.sort(key=lambda x: x.rank, reverse=True)
        self._players.sort(key=lambda x: x.elo, reverse=True)
        ident = 1
        for player in self._players:
            if not player.pauser:
                player.id = ident
                self.sql.update_player_info(
                    name=player.name, surname=player.surname, nr=player.id
                )
                ident += 1
        system = get_system(self._system)
        # Store player IDs BEFORE system preparation
        player_id_map = {p.name: p.id for p in self._players if p.id > 0}
        self._rounds.append(system.prepare_round(self._players, self._act_round_nr))
        # Merge back: keep all players, update active ones from system
        active_ids = {p.id for p in system.players}
        updated_players = list(system.players)
        for p in self._players:
            if p.id not in active_ids and not p.pauser:
                updated_players.append(p)
        self._players = updated_players
        # Restore original player IDs after system preparation
        for player in self._players:
            if player.name in player_id_map:
                player.id = player_id_map[player.name]
        # Save pairings for the first round to DB
        self._save_round_pairings(self._act_round_nr)

    def load_results(self):
        """Load results and rebuild rounds from DB-saved pairings for repeatability."""
        if self._act_round_nr <= 0:
            logging.debug("No tournament started yet, skipping load_results")
            return

        system = get_system(self._system)
        if system is None:
            logging.error("System is not properly set, cannot load results")
            return

        self.fine_to_begin = True
        data = self.sql.read_results_info()
        logging.debug(
            f"Loaded results data consists info:\n"
            f" - actual round nr:  {self._act_round_nr}\n"
            f" - turnament rounds: {self._rounds_num}\n"
            f" - games:            {len(data)}\n"
        )
        if self._act_round_nr <= 0:
            return

        target_round_nr = self._act_round_nr

        for r in range(1, target_round_nr + 1):
            self._act_round_nr = r

            # Always try to load pairings from DB first for repeatability
            _round = self._load_round_pairings(r)
            if _round is None:
                # No saved pairings - generate them (first time scenario)
                logging.info(f"Round #{r}: no DB pairings, generating fresh.")
                _round = system.prepare_round(self._players, r)
                # Merge players back from system
                active_ids = {p.id for p in system.players}
                updated_players = list(system.players)
                for p in self._players:
                    if p.id not in active_ids and not p.pauser:
                        updated_players.append(p)
                self._players = updated_players

            if not _round.tables:
                logging.warning(f"Round #{r}: no tables after load, generating.")
                _round = system.prepare_round(self._players, r)

            logging.debug(
                f"Round #{r}: loaded with {len(_round.tables)} tables, "
                f"pausing={_round.pausing}"
            )

            # Apply saved results for this round
            _results = [result for result in data if result.get("round") == r]
            for result in _results:
                table_nr = result["table"]
                if table_nr in _round.tables:
                    _round.set_result(table_nr=table_nr, result=result["result"])
                else:
                    logging.warning(
                        f"Table {table_nr} not found in round {r}. Skipping."
                    )

            # Store round
            if len(self._rounds) >= r:
                self._rounds[r - 1] = _round
            else:
                self._rounds.append(_round)

            # If round is complete, apply results for player scoring
            if _round.all_results or (self._finished and r < target_round_nr):
                self.apply_round_results()
                self._save_round_pairings(r)
                self._finished_round_nr = r

        # Restore actual round number
        self._act_round_nr = target_round_nr

        if self._finished:
            self._finished_round_nr = target_round_nr

        self.sql.update_turnament_info(
            roundactual=self._act_round_nr, roundfinished=self._finished_round_nr
        )

    def next_round(self):
        _ret = None
        if self._act_round_nr < self._rounds_num:
            # Save pairings and pause info for the current round before moving to the next
            self._save_round_pairings(self._act_round_nr)

            self._act_round_nr += 1
            self._finished_round_nr = self._act_round_nr - 1

            # Try to load pairings from DB first
            loaded_pairings = self._load_round_pairings(self._act_round_nr)
            if loaded_pairings:
                # Use loaded pairings instead of creating new ones
                self._rounds.append(loaded_pairings)
                msg_info = f"Round {self._act_round_nr} pairings loaded from DB"
                logging.info(msg=msg_info)
            else:
                # Create new pairings if not in DB - use ALL players
                # (system.prepare_round filters suspended ones internally)
                system = get_system(self._system)
                self._rounds.append(
                    system.prepare_round(self._players, self._act_round_nr)
                )
                # Merge back: keep all players, update active ones from system
                active_ids = {p.id for p in system.players}
                updated_players = list(system.players)
                for p in self._players:
                    if p.id not in active_ids and not p.pauser:
                        updated_players.append(p)
                self._players = updated_players
                # Save new pairings to DB immediately
                self._save_round_pairings(self._act_round_nr)
            _ret = None
        else:
            _ret = -1
            self._finished_round_nr = self._act_round_nr
            self._finished = True
            self.sql.update_turnament_info(finished=self._finished)
            msg_error = (
                f"Maximum turnament round: {self._rounds_num}!!"
                " *** Turnament finished ***"
            )
            logging.info(msg=msg_error)
        self.sql.update_turnament_info(
            roundactual=self._act_round_nr, roundfinished=self._finished_round_nr
        )
        return _ret

    def apply_round_results(self):
        # Handle if wrong type passed
        if not self.fine_to_begin:
            msg_error = "Round cannot be started. Check turnament settings."
            logging.error(msg=msg_error)
            return None
        elif not self._rounds[self._act_round_nr - 1].all_results:
            msg_error = f"Not all results have been applied yet! {self._rounds[self._act_round_nr - 1].dump()}"
            logging.error(msg=msg_error)
            return None
        _round = self._rounds[self._act_round_nr - 1]
        if not isinstance(_round, Round):
            return None
        # Finish turnament flag:
        if self._act_round_nr == self._rounds_num:
            self._finished = True
        # Move results of tables to player scores:
        for t_key in _round.tables:
            table = _round.tables[t_key]

            msg_debug = "Check table.dump():"
            logging.debug(msg=msg_debug)
            logging.debug(msg=table.dump())

            for player in self._players:
                if player.id == table.w_player.id and player.id != _round.pausing:
                    player.points += table.result
                    player.progress += player.points
                    player.add_opponent(table.b_player.id)
                    player.add_result(table.result)
                    player.round_done = True
                if player.id == table.b_player.id and player.id != _round.pausing:
                    player.points += 1.0 - table.result
                    player.progress += player.points
                    player.add_opponent(table.w_player.id)
                    player.add_result(1.0 - table.result)
                    player.round_done = True
        if _round.pausing > 0:
            for player in self._players:
                if player.id == _round.pausing and player.id > 0:
                    player.points += 1
                    player.progress += player.points
                    player.add_opponent(-1)
                    player.add_result(1.0)
                    msg_debug = f"Pausing: #{_round.pausing}"
                    logging.debug(msg=msg_debug)
        # Calculate bucholz for each player after the round:
        for player in self._players:
            _bucholz = 0.0
            for opponent_idnt in player.opponents:
                for opponent in self._players:
                    if opponent.id == opponent_idnt:
                        _bucholz += opponent.points
            player.bucholz = _bucholz
        # Sort players:
        self._players.sort(key=lambda x: x.bucholz, reverse=True)
        self._players.sort(key=lambda x: x.progress, reverse=True)
        self._players.sort(key=lambda x: x.points, reverse=True)

    def delete_players(self):
        if self._players:
            self._players.clear()

    def get_players(self, type="results"):
        data = {"quantity": len(self._players), "players": []}
        specific = []
        _type = type.lower()
        if _type in ("results", "result"):
            specific = [
                "id",
                "name",
                "surname",
                "cat",
                "elo",
                "club",
                "city",
                "sex",
                "rank",
                "result",
                "progress",
                "bucholz",
            ]
        elif _type in ("start", "init"):
            specific = [
                "id",
                "name",
                "surname",
                "cat",
                "elo",
                "club",
                "city",
                "sex",
                "rank",
            ]
        elif _type in ("name", "names", "fullname", "fullnames"):
            specific = ["id", "name", "surname"]
        else:
            return {
                "error": 'Please use one of following types: "results", "init", "names"'
            }
        for player in self._players:
            data["players"].append(player.get(specific=specific))
        if type in ("start", "init"):
            data["players"].sort(key=lambda x: x["id"], reverse=True)
            data["players"].sort(key=lambda x: x["rank"], reverse=True)
            data["players"].sort(key=lambda x: x["elo"], reverse=True)
            _nr = 1
            for player in data["players"]:
                player["nr"] = _nr
                _nr += 1
        else:
            data["players"].sort(key=lambda x: x["progress"], reverse=True)
            data["players"].sort(key=lambda x: x["bucholz"], reverse=True)
            data["players"].sort(key=lambda x: x["result"], reverse=True)
        return data

    def get_suspended_players(self, round_nr):
        """Return list of players suspended for a given round."""
        return [p for p in self._players if p.is_suspended(round_nr) and not p.pauser]

    def dump_act_results(self):
        _dump = f"RESULTS AFTER ROUND NR: #{self._act_round_nr}:\n\n"
        _dump1 = "#Id:  PLAYER: "
        _dump2 = "\tPTS:  \tPROG:  \tBUCH: \tRANK: \tCAT:\n"
        _dump += "{0:<34}".format(_dump1) + _dump2
        for player in self._players:
            _dump1 = f"#{player.id}    {player.surname} {player.name}: "
            _dump2 = (
                f"\t{player.points}  \t{player.progress}  \t{player.bucholz} "
                f"\t{player.rank} \t{player.category}\n"
            )
            _dump += "{0:<34}".format(_dump1) + _dump2
        return _dump

    def dump_players(self):
        _dump = "PLAYERS - LIST:"
        for player in self._players:
            _dump += player.dump()
            _dump += player.dump_opponents()
        return _dump

    def dump_players_p_o(self):
        _dump = "PLAYERS - POSSIBLE OPPONENTS:\n"
        for player in self._players:
            _dump += player.dump_possible_opponents()
        return _dump

    def get(self):
        return {
            "name": self._name,
            "place": self._place,
            "players": self.players_num,
            "rounds": self._rounds_num,
            "actual": self._act_round_nr,
            "finished": self._finished,
            "system": SystemNames[self._system],
        }

    def _save_round_pairings(self, round_nr):
        """Save pairings and pause info for a completed round to DB."""
        if round_nr > 0 and round_nr <= len(self._rounds):
            _round = self._rounds[round_nr - 1]
            # Save pairings for each table
            for table_nr in _round.tables:
                table = _round.tables[table_nr]
                # Replace pausing player (-1) with 0 for DB storage
                player_w_id = table.w_player.id if table.w_player.id > 0 else 0
                player_b_id = table.b_player.id if table.b_player.id > 0 else 0

                # Only save if at least one real player exists
                if player_w_id > 0 or player_b_id > 0:
                    self.sql.insert_pairing(
                        round=round_nr,
                        table=table_nr,
                        player_w=player_w_id,
                        player_b=player_b_id,
                    )
            # Save pause info if there's a pausing player
            if _round.pausing > 0:
                self.sql.insert_pause(
                    round=round_nr,
                    player_id=_round.pausing,
                )
            msg_info = f"Pairings for round {round_nr} saved to DB"
            logging.info(msg=msg_info)

    def _load_round_pairings(self, round_nr):
        """Load pairings for a round from DB and rebuild the Round object."""
        pairings = self.sql.read_pairings_info()
        round_pairings = [p for p in pairings if p.get("round") == round_nr]

        # Check for pause info
        pauses = self.sql.read_pauses_info()
        round_pause = next((p for p in pauses if p.get("round") == round_nr), None)
        pausing_player_id = round_pause.get("player_id", 0) if round_pause else 0

        # If no pairings found, return None (pause alone is not enough to rebuild a round)
        if not round_pairings:
            msg_debug = f"No saved pairings found for round {round_nr}"
            logging.debug(msg=msg_debug)
            return None

        # Create a new Round object from saved pairings
        _round = Round(number=round_nr)
        _round.pausing = pausing_player_id

        # Create player objects from current player list
        player_map = {p.id: p for p in self._players}

        # Create pausing player (fantom) for later use
        pausing_player = Player(pauser=True) if pausing_player_id > 0 else None

        # Sort pairings by table number to ensure correct order
        round_pairings.sort(key=lambda x: x.get("table", 0))

        # Rebuild tables from saved pairings — directly assign to tables dict
        # to avoid add_table() swap logic that changes table numbering
        for pairing in round_pairings:
            table_nr = pairing.get("table")
            player_w_id = pairing.get("player_w")
            player_b_id = pairing.get("player_b")

            # Handle player IDs (0 means pausing player, which we'll treat as fantom)
            player_w = player_map.get(player_w_id) if player_w_id > 0 else None
            player_b = player_map.get(player_b_id) if player_b_id > 0 else None

            # If one of the players is 0 (pausing player), use fantom
            if player_w_id == 0 and pausing_player:
                player_w = pausing_player
            if player_b_id == 0 and pausing_player:
                player_b = pausing_player

            # At least one player must be found
            if (player_w_id > 0 and not player_w) or (player_b_id > 0 and not player_b):
                msg_error = (
                    f"Could not find player for table {table_nr} in round {round_nr}"
                )
                logging.error(msg=msg_error)
                return None

            # Both players must exist — create table directly to preserve numbering
            if player_w and player_b:
                table = Table(number=table_nr, w_player=player_w, b_player=player_b)
                _round.tables[table_nr] = table
                # Set auto-result for pauser tables
                if player_w.id == -1:
                    _round.set_result(table_nr=table_nr, result=0.0)
                elif player_b.id == -1:
                    _round.set_result(table_nr=table_nr, result=1.0)

        msg_info = f"Round {round_nr} successfully loaded from DB with {len(round_pairings)} pairings"
        if pausing_player_id > 0:
            msg_info += f" and pausing player #{pausing_player_id}"
        logging.info(msg=msg_info)

        # If no tables were actually built, return None so caller can regenerate
        if not _round.tables:
            logging.warning(
                f"Round {round_nr}: pairings found in DB but no tables could be rebuilt. "
                f"Will regenerate pairings."
            )
            return None

        return _round

    def dump(self):
        _dump = f"TURNAMENT: {self._name}\n"
        _dump += f" Place: {self._place}\n"
        # _dump += f'Time: {self._date_start} to {self._date_end}\n\n'
        _dump += f" Players: {self.players_num}\n"
        _dump += f" System: {SystemNames[self._system]}\n"
        _dump += f" Round actual: {self._act_round_nr}\n"
        _dump += f" Rounds: {self._rounds_num}\n"
        if self._act_round_nr and len(self._rounds):
            _dump += self._rounds[self._act_round_nr - 1].dump()
        return _dump

    def __repr__(self) -> str:
        return self.dump().replace("\n", ",")
