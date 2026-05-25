"""actions.py

Application action class with actions over the app instance
i.e. open, close, add player, modify, ...

@WARNING:
Actions have one instance only over the app (singleton)
and one layer before any API way (CLI, restAPI).

"""

# noqa: F401
# Global package imports:
import logging
from functools import cache

# Local package imports:
import Resources
from Application.browser import Browser
from Application.logger import log_method
from Application.turnament import Turnament
from Templates.round import RoundView

# Third party imports:
from starlette.responses import FileResponse


@cache
class Actions:
    """Actions over turnament process, state, players and file handler."""

    def __init__(self, name):
        self._name = name
        self._end = False
        self._is_browser_opened = False
        self._is_opened = False
        self._cmd = None
        self.turnament = None
        self.sql_engine = None
        msg = f'Starting actions core for "{name}" application.. '
        logging.info(msg)
        self.browser = Browser()

    def app_status(self):
        log_method(obj=self, func=self.app_status)
        turnament = self.turnament.get() if self.turnament else None
        data = {"status": self._is_opened, "turnament": turnament}
        logging.info("App status. Content data: \n{}".format(data))
        return data

    def app_info(self):
        log_method(obj=self, func=self.app_info)
        data = {"name": Resources.APPLICATION_NAME, "version": Resources.__version__}
        logging.info("App info. Content data: \n{}".format(data))
        return data

    def open(self, name: str, cmd: str, path: str = ""):
        log_method(obj=self, func=self.open)
        if name:
            if cmd == "New":
                self.browser.set_file(filename=name, path=path)
            self.browser.get_file(option=cmd, path=path)
            self.turnament = Turnament(name=name, engine=self.browser.engine)
            self._is_opened = True
        data = {"status": self._is_opened, "turnament": self.turnament.get()}
        logging.info(f'Opened turnament "{name}". Content data: \n{data}')
        return data

    def get_files(self, path: str = ""):
        log_method(obj=self, func=self.get_files)
        data = self.browser.get_file_list(path=path)
        logging.debug(f"Tournament files list: \n{data}")
        return data

    def remove_files(self, tournament_name: str = ""):
        log_method(obj=self, func=self.remove_files)
        self.browser.remove_tournament_from_list(tournament_name)
        logging.info(f'Tournament "{tournament_name}" files removed')
        return True

    def close(self):
        log_method(obj=self, func=self.close)
        self.browser.stop()
        self.turnament.delete_players()
        self._is_opened = False
        self.turnament = None

    def end(self):
        log_method(obj=self, func=self.end)
        self._end = True

    def turnament_start(self, system_type: str, rounds=0):
        if system_type.lower() in "swiss":
            if rounds == 0:
                logging.error("Set number of rounds to play!")
                return
            s_type = Resources.SystemType.SWISS
        elif system_type.lower() in "circular":
            s_type = Resources.SystemType.CIRCULAR
            rounds = self.turnament.players_num - 1
        elif system_type.lower() in "elimination":
            s_type = Resources.SystemType.SINGLE_ELIMINATION
        else:
            logging.error("Wrong turnament system typed! {}".format(system_type))
            return
        self.turnament.set_system(system_id=s_type)
        self.turnament.begin(rounds=rounds)
        data = {"status": True, "turnament": self.turnament.get()}
        logging.info("Turnament begun. Content data: \n{}".format(data))
        return data

    def player_add(
        self, name="", surname="", sex="male", city="", category="wc", elo=0
    ):
        log_method(obj=self, func=self.player_add)
        if not self.turnament:
            logging.error("No turnament active. Please start turnament.")
            data = {"status": False, "player": None}
        else:
            self.turnament.add_player(
                name=name,
                surname=surname,
                sex=sex,
                city=city,
                category=category,
                elo=elo,
            )
            data = {"status": True, "player": str(self.turnament._players[-1])}
        logging.info("Player added. Content data: \n{}".format(data))
        return data

    def player_del(self, name="", surname=""):
        log_method(obj=self, func=self.player_del)
        if not self.turnament:
            logging.error("No turnament active. Please start turnament.")
            data = {"status": False}
        else:
            data = {"status": self.turnament.del_player(name=name, surname=surname)}
        logging.info("Player deleted. Content data: \n{}".format(data))
        return data

    def player_edit(
        self,
        player_id: int,
        name="",
        surname="",
        sex="male",
        city="",
        category="wc",
        elo=0,
    ):
        log_method(obj=self, func=self.player_edit)
        if not self.turnament:
            logging.error("No turnament active.")
            return {"status": False}

        for p in self.turnament._players:
            if p.id == player_id:
                old_name = p.name
                old_surname = p.surname
                p.name = name
                p.surname = surname
                p.sex = sex
                p.city = city
                p.category = category
                p.elo = int(elo) if elo else 0
                p.calculate_rank()
                self.turnament.sql.update_player_info(
                    name=old_name, surname=old_surname, nr=player_id
                )
                self.turnament.sql.remove_player_info(
                    name=old_name, surname=old_surname
                )
                self.turnament.sql.insert_player_info(
                    name=name,
                    surname=surname,
                    sex=sex,
                    city=city,
                    category=category,
                    elo=int(elo) if elo else 0,
                )
                self.turnament.sql.update_player_info(
                    name=name, surname=surname, nr=player_id
                )
                logging.info(f"Player #{player_id} updated: {name} {surname}")
                return {"status": True}

        logging.error(f"Player #{player_id} not found.")
        return {"status": False}

    def players_get(self, type="results", log_action=True):
        log_method(obj=self, func=self.players_get)
        if not self.turnament:
            logging.error(
                "No turnament active. Please start turnament and add Players."
            )
            data = {"status": False, "players": None}
        else:
            data = {"status": True, "players": self.turnament.get_players(type=type)}
        if log_action:
            logging.info("Players content data: \n{}".format(data))
        return data

    def turnament_results(self):
        log_method(obj=self, func=self.turnament_results)
        if not self.turnament:
            logging.error(
                "No turnament active. Please start turnament and add Players."
            )
            data = {"status": False, "round": None, "players": None}
        else:
            data = {
                "status": True,
                "round": self.turnament._act_round_nr,
                "players": self.players_get(type="results", log_action=False)[
                    "players"
                ],
            }
        logging.info("Results content data: \n{}".format(data))
        return data

    def player_stats(self, player_id: int):
        """Get detailed statistics for a player including per-round ELO changes."""
        log_method(obj=self, func=self.player_stats)
        if not self.turnament:
            return {"status": False, "player": None}

        player = None
        for p in self.turnament._players:
            if p.id == player_id:
                player = p
                break
        if not player:
            return {"status": False, "player": None}

        K = 20  # ELO K-factor for calculation
        rounds_data = []
        total_elo_change = 0.0

        # Build a map of actual round numbers to opponent/result entries
        # by checking which rounds this player was active in
        active_rounds = []
        for r_idx, rd in enumerate(self.turnament._rounds):
            round_nr = r_idx + 1
            # Check if player was in this round's tables or was pausing
            player_in_round = False
            if rd.pausing == player_id:
                player_in_round = True
            else:
                for _, table in rd.tables.items():
                    if table.w_player.id == player_id or table.b_player.id == player_id:
                        player_in_round = True
                        break
            if player_in_round:
                active_rounds.append(round_nr)

        for i, (opp_id, result) in enumerate(zip(player.opponents, player.results)):
            # Map index to actual round number
            round_nr = active_rounds[i] if i < len(active_rounds) else i + 1
            opponent = None
            opponent_elo = 0
            color = "white"

            if opp_id == -1:
                rounds_data.append(
                    {
                        "round_nr": round_nr,
                        "opponent_name": "Bye",
                        "opponent_elo": 0,
                        "color": "-",
                        "result": result,
                        "elo_change": 0.0,
                    }
                )
                continue

            for op in self.turnament._players:
                if op.id == opp_id:
                    opponent = op
                    opponent_elo = op.elo
                    break

            # Determine color played
            if round_nr <= len(self.turnament._rounds):
                rd = self.turnament._rounds[round_nr - 1]
                for _, table in rd.tables.items():
                    if table.w_player.id == player_id:
                        color = "white"
                        break
                    elif table.b_player.id == player_id:
                        color = "black"
                        break

            # Calculate ELO change
            elo_change = 0.0
            if player.elo > 0 and opponent_elo > 0 and result >= 0:
                expected = 1.0 / (1.0 + 10 ** ((opponent_elo - player.elo) / 400.0))
                elo_change = K * (result - expected)
                total_elo_change += elo_change

            opp_name = (opponent.surname + " " + opponent.name) if opponent else "?"

            rounds_data.append(
                {
                    "round_nr": round_nr,
                    "opponent_name": opp_name,
                    "opponent_elo": opponent_elo,
                    "color": color,
                    "result": result,
                    "elo_change": round(elo_change, 1),
                }
            )

        data = {
            "status": True,
            "player": {
                "id": player.id,
                "name": player.name,
                "surname": player.surname,
                "elo": player.elo,
                "cat": player.category,
                "points": sum(player.results) if player.results else 0.0,
                "bucholz": player.bucholz,
                "progress": player.progress,
                "elo_change": round(total_elo_change, 1),
                "rounds": rounds_data,
            },
        }
        return data

    def players_suspend_list(self):
        """Get list of players with their suspend status for the next round."""
        log_method(obj=self, func=self.players_suspend_list)
        if not self.turnament:
            return {"status": False, "players": []}

        next_round = self.turnament._act_round_nr + 1
        players = []
        for p in self.turnament._players:
            if p.pauser or p.id <= 0:
                continue
            players.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "surname": p.surname,
                    "cat": p.category,
                    "elo": p.elo,
                    "suspended": p.is_suspended(next_round),
                }
            )
        return {"status": True, "players": players}

    def players_suspend(self, suspended: list, unsuspended: list):
        """Apply suspend/unsuspend for players from next round onwards."""
        log_method(obj=self, func=self.players_suspend)
        if not self.turnament:
            return {"status": False}

        next_round = self.turnament._act_round_nr + 1
        max_round = self.turnament._rounds_num

        for p in self.turnament._players:
            if p.id in suspended:
                for r in range(next_round, max_round + 1):
                    p.suspend_player(r)
                logging.info(f"Player #{p.id} suspended from round {next_round}")
            elif p.id in unsuspended:
                for r in range(next_round, max_round + 1):
                    p.suspended_rounds.discard(r)
                logging.info(f"Player #{p.id} unsuspended from round {next_round}")

        return {"status": True}

    def turnament_round(self, nr=0, full=True):
        log_method(obj=self, func=self.turnament_round)
        nr = int(nr) - 1
        if not self.turnament:
            logging.error("No turnament active. Please start turnament with Players.")
            data = {"status": False, "round": None}
        elif nr == -1 or nr in range(len(self.turnament._rounds)):
            data = {"status": True, "round": self.turnament._rounds[nr].get(full=full)}
            # Resolve pauser info - show actual player data if pauser exists
            if "pauser" in data["round"] and data["round"]["pauser"] > 0:
                p_id = data["round"]["pauser"]
                pauser_found = False
                for player in self.turnament._players:
                    if player.id == p_id:
                        data["round"]["pauser"] = player.get(
                            specific=["id", "name", "surname", "cat", "elo"]
                        )
                        pauser_found = True
                        break
                if not pauser_found:
                    data["round"]["pauser"] = None
            else:
                data["round"]["pauser"] = None

            # Add suspended players info for this round
            round_nr = nr + 1 if nr >= 0 else len(self.turnament._rounds)
            suspended = self.turnament.get_suspended_players(round_nr)
            # Filter out the pauser from suspended list to avoid duplication
            pauser_id = self.turnament._rounds[nr].pausing if nr >= 0 else 0
            suspended = [p for p in suspended if p.id != pauser_id]
            if suspended:
                data["round"]["suspended"] = [
                    p.get(specific=["id", "name", "surname", "cat", "elo"])
                    for p in suspended
                ]
            else:
                data["round"]["suspended"] = []
            logging.debug("Rounds: \n{}".format(self.turnament._rounds))
        else:
            logging.error("Wrong round number.")
            data = {"status": False, "round": None}
        logging.info("Round content data: \n{}".format(data))
        return data

    def turnament_round_to_html(self, nr=0, full=True):
        log_method(obj=self, func=self.turnament_round_to_html)
        data = self.turnament_round(nr=nr, full=full)
        web = RoundView(data=data)
        web.update()
        location, file_name = self.browser.add_or_update_extra_file(
            filename=web.destination_name, content=web._template
        )
        return FileResponse(
            location, media_type="application/octet-stream", filename=file_name
        )

    def set_round_result(self, table_nr: int, result: float):
        log_method(obj=self, func=self.set_round_result)
        if not self.turnament:
            logging.error(
                "No turnament active. Please start turnament and add Players."
            )
            data = {"status": False}
        else:
            data = {"status": True}
            self.turnament.add_result(table_nr=table_nr, result=result)
        logging.info(f"Table {table_nr} result ({result}) changed.")
        return data

    def apply_round(self):
        log_method(obj=self, func=self.apply_round)
        round_nr = len(self.turnament._rounds)
        if self.turnament._rounds[round_nr - 1].all_results:
            logging.info(f"Round {round_nr} applied.")
            self.turnament.apply_round_results()
            self.turnament.next_round()
            return True
        else:
            logging.error(f"Round {round_nr} NOT applied. Still awaiting results!")
            return False

    def debug_method(self):
        """Debugging purpose only.
        This example holds simple swiss system simulation (one manual test case), but critical.
        There are 6 rounds for 7 Players.
        Remarks:
         - Swiss system transform into circular.
         - Pause must be every round counted.
        """
        log_method(obj=self, func=self.debug_method)
        self.player_add(
            name="Jacob",
            surname="K",
            sex="male",
            city="Bedzin",
            category="III",
            elo=0,
        )
        self.player_add(
            name="Joannah",
            surname="K",
            sex="female",
            city="Bedzin",
            category="bk",
            elo=0,
        )
        self.player_add(
            name="Jaroslaw",
            surname="Katchynsky",
            sex="male",
            city="Nowogrodzka",
            category="bk",
            elo=0,
        )
        self.player_add(
            name="Mateush",
            surname="Morawitz",
            sex="male",
            city="Warsaw",
            category="IV",
            elo=0,
        )
        self.player_add(
            name="Adam",
            surname="Malysh",
            sex="male",
            city="Wisla",
            category="II",
            elo=1755,
        )
        self.player_add(
            name="Piotr",
            surname="Zyla",
            sex="male",
            city="Zakopane",
            category="V",
            elo=0,
        )
        self.player_add(
            name="Mario",
            surname="Super",
            sex="male",
            city="Pilsudsky Square",
            category="bk",
            elo=1355,
        )
        msg_debug = "ROUND #1:"
        logging.debug(msg=msg_debug)
        self.turnament.set_system(system_id=Resources.SystemType.SWISS)
        self.turnament.begin(rounds=6)
        self.turnament.add_result(table_nr=1, result=1.0)
        self.turnament.add_result(table_nr=2, result=1.0)
        self.turnament.add_result(table_nr=3, result=0.5)
        self.turnament.apply_round_results()
        logging.debug(msg=self.turnament.dump_act_results())
        # logging.debug(msg=self.turnament.dump_players())

        msg_debug = "ROUND #2:"
        logging.debug(msg=msg_debug)
        self.turnament.next_round()
        # logging.debug(msg=self.turnament.dump())
        self.turnament.add_result(table_nr=1, result=0.5)
        self.turnament.add_result(table_nr=2, result=0.0)
        self.turnament.add_result(table_nr=3, result=1.0)
        self.turnament.apply_round_results()
        logging.debug(msg=self.turnament.dump_act_results())
        # logging.debug(msg=self.turnament.dump_players())

        msg_debug = "ROUND #3:"
        logging.debug(msg=msg_debug)
        self.turnament.next_round()
        # logging.debug(msg=self.turnament.dump())
        self.turnament.add_result(table_nr=1, result=0.5)
        self.turnament.add_result(table_nr=2, result=0.0)
        self.turnament.add_result(table_nr=3, result=1.0)
        self.turnament.apply_round_results()
        logging.debug(msg=self.turnament.dump_act_results())
        # logging.debug(msg=self.turnament.dump_players())

        msg_debug = "ROUND #4:"
        logging.debug(msg=msg_debug)
        self.turnament.next_round()
        # logging.debug(msg=self.turnament.dump())
        self.turnament.add_result(table_nr=1, result=0.5)
        self.turnament.add_result(table_nr=2, result=0.5)
        self.turnament.add_result(table_nr=3, result=1.0)
        self.turnament.apply_round_results()
        logging.debug(msg=self.turnament.dump_act_results())
        # # logging.debug(msg=self.turnament.dump_players())

        msg_debug = "ROUND #5:"
        logging.debug(msg=msg_debug)
        self.turnament.next_round()
        # logging.debug(msg=self.turnament.dump())
        self.turnament.add_result(table_nr=1, result=0.5)
        self.turnament.add_result(table_nr=2, result=0.0)
        self.turnament.add_result(table_nr=3, result=1.0)
        self.turnament.apply_round_results()
        logging.debug(msg=self.turnament.dump_act_results())
        # logging.debug(msg=self.turnament.dump_players_p_o())

        msg_debug = "ROUND #6:"
        logging.debug(msg=msg_debug)
        self.turnament.next_round()
        # logging.debug(msg=self.turnament.dump())
        self.turnament.add_result(table_nr=1, result=0.5)
        self.turnament.add_result(table_nr=2, result=0.0)
        self.turnament.add_result(table_nr=3, result=0.0)
        self.turnament.apply_round_results()
        logging.debug(msg=self.turnament.dump_act_results())
        # # logging.debug(msg=self.turnament.dump_players())
