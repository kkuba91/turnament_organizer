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
from Systems import get_system
from resources import SystemType, SystemNames
from Application.sql_utils import SqlUtils


class Turnament(object):
    def __init__(self, name, engine) -> None:
        # General:
        self._name = name
        self._date_start = date.today()
        self._date_end = None
        self._players_num = 0
        self._mean_rank = 0
        self._mean_age = 0
        self._rounds_num = 0
        self._act_round_nr = 0
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
        # Initialize turnament table data:
        self.sql.turnament_init()
        self.sql.update_turnament_info(name=self._name,
                                       date_start=self._date_start,
                                       system=self._system)
        info = self.sql.read_turnament_info()[0]
        self._rounds_num = info.get("rounds") if info.get("rounds") else 0
        self._date_start = info.get("datestart")
        self._date_end = info.get("dateend")
        self._act_round_nr = info.get("roundactual") if info.get("roundactual") else 0
        self._place = info.get("place")
        self._system = info.get("system") if info.get("system") else SystemType.UNKNOWN
        # Initialize Players data from db:
        players = self.sql.read_players_info()
        players.sort(key=lambda x: x.get("nr") if x.get("nr") else 0, reverse=False)
        for player in players:
            self.add_player(
                _id=player.get("nr"),
                name=player.get("name"),
                surname=player.get("surname"),
                sex=player.get("sex"),
                city=player.get("city"),
                category=player.get("category"),
                elo=player.get("elo"),
                insert_to_db=False
            )
        # Initialize Rounds data from db:
        # @ToDo: Implement rounds data loading
        # sql.read_rounds_info()
        self.load_rounds()


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
        self, name="", surname="", sex="male", city="", category="bk", elo=0, _id=None, insert_to_db=True
    ):
        # Validate Player add:
        _dont_add = False
        for p in self._players:
            if p.name == name and p.surname == surname:
                _dont_add = True
                msg_error_1 = f"\nPlayer {name} {surname} already set into turnament."
                logging.error(msg=msg_error_1)
        # Add Player:
        if not _dont_add:
            try:
                player = Player(
                    name=name,
                    surname=surname,
                    sex=sex,
                    city=city,
                    category=category,
                    elo=elo
                )
            except ValidationError as exc:
                msg_error_2 = f"\nCannot add Player {name} {surname} with invalid data."
                logging.error(msg=str(exc) + msg_error_2)
            else:
                if _id:
                    player.id = _id
                self._players.append(player)
                if insert_to_db:
                    self.sql.insert_player_info(name=name,
                                                surname=surname,
                                                sex=sex,
                                                city=city,
                                                category=category,
                                                elo=elo)
                msg_info = f"Set Player: {player.name} {player.surname}, " + \
                           f"[elo: {player.elo}, cat: {player.category}] in turnament."
                logging.info(msg=msg_info)

    def del_player(self, name="", surname=""):
        for player in self._players:
            if player.exist(name=name, surname=surname):
                msg_info = f"Remove: {player.name} " + \
                           f"{player.surname} from turnament."
                logging.info(msg=msg_info)
                self._players.pop(player)
                self.sql.remove_player_info(name=name,
                                            surname=surname)
            else:
                msg_info = f"No Player #{player.id} on turnament list."
                logging.info(msg=msg_info)

    def add_result(self, table_nr, result):
        round_id = self._act_round_nr - 1
        if self.fine_to_begin:
            try:
                self._rounds[round_id].set_result(table_nr, result)
            except KeyError as exc:
                msg_error = f"Used values: round_id={round_id}, table_nr={table_nr}. ({exc})"
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
                self.sql.update_player_info(name=player.name,
                                            surname=player.surname,
                                            nr=player.id)
                ident += 1
        system = get_system(self._system)
        self._rounds.append(system.prepare_round(self._players, self._act_round_nr))
        self._players = system.players

    def load_rounds(self):
        # @ToDo: Add loading to Rounds here
        system = get_system(self._system)
        # self._players = system.players

    def next_round(self):
        _ret = None
        if self._act_round_nr < self._rounds_num:
            self._act_round_nr += 1
            system = get_system(self._system)
            self._rounds.append(system.prepare_round(self._players, self._act_round_nr))
            self._players = system.players
            _ret = None
        else:
            _ret = -1
            msg_error = f"Maximum turnament round: {self._rounds_num}!!"
            logging.error(msg=msg_error)
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
        # Move results of tables to player scores:
        for t_key in _round.tables:
            table = _round.tables[t_key]

            msg_debug = "Check table.dump():"
            logging.debug(msg=msg_debug)
            logging.debug(msg=table.dump())

            for player in self._players:
                if player.id == table.w_player and player.id != _round.pausing:
                    player.points += table.result
                    player.progress += player.points
                    player.add_opponent(table.b_player)
                    player.add_result(table.result)
                    player.round_done = True
                if player.id == table.b_player and player.id != _round.pausing:
                    player.points += 1.0 - table.result
                    player.progress += player.points
                    player.add_opponent(table.w_player)
                    player.add_result(1.0 - table.result)
                    player.round_done = True
        if _round.pausing > 0:
            for player in self._players:
                if player.id == _round.pausing and player.id > 0:
                    player.points += 1
                    player.progress += player.points
                    player.add_opponent(-1)
                    player.add_result(1.0)
                    msg_debug = f"Pausing: #{ _round.pausing}"
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

    def get_players(self, type='results'):
        data = {
            'quantity': len(self._players),
            'players': []
        }
        specific = []
        _type = type.lower()
        if _type in ('results', 'result'):
            specific = ['id', 'name', 'surname', 'cat', 'elo', 'result', 'progress', 'bucholz']
        elif _type in ('start', 'init'):
            specific = ['id', 'name', 'surname', 'cat', 'elo', 'club', 'city', 'sex']
        elif _type in ('name', 'names', 'fullname', 'fullnames'):
            specific = ['id', 'name', 'surname']
        else:
            return {'error': 'Please use one of following types: "results", "init", "names"'}
        for player in self._players:
            data["players"].append(player.get(specific=specific))
        if type in ('start', 'init'):
            data["players"].sort(key=lambda x: x['id'], reverse=True)
        else:
            data["players"].sort(key=lambda x: x['bucholz'], reverse=True)
            data["players"].sort(key=lambda x: x['progress'], reverse=True)
            data["players"].sort(key=lambda x: x['result'], reverse=True)
        return data

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
            'name': self._name,
            'place': self._place,
            'players': self.players_num,
            'rounds': self._rounds_num,
            'actual': self._act_round_nr,
            'system': SystemNames[self._system]
        }

    def dump(self):
        _dump = f"TURNAMENT: {self._name}\n"
        _dump += f" Place: {self._place}\n"
        # _dump += f'Time: {self._date_start} to {self._date_end}\n\n'
        _dump += f" Players: {self.players_num}\n"
        _dump += f" System: {SystemNames[self._system]}\n"
        _dump += f" Round actual: {self._act_round_nr}\n"
        _dump += f" Rounds: {self._rounds_num}\n"
        if self._act_round_nr > 0:
            _dump += self._rounds[self._act_round_nr - 1].dump()
        return _dump

    def __repr__(self) -> str:
        return self.dump().replace('\n', ',')
