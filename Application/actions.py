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
from Application.browser import Browser
from Application.logger import log_method
from Application.turnament import Turnament
import Resources


@cache
class Actions:

    """Actions over turnament process, state, players and file handler."""
    def __init__(self, name):
        self._name = name
        self._end = False
        self._is_db_opened = False
        self._is_browser_opened = False
        self._is_opened = False
        self._cmd = None
        self._turnament = None
        msg = f'Starting actions core for "{name}" application.. '
        logging.info(msg)
        self._browser = Browser()


    def app_status(self):
        log_method(obj=self, func=self.app_status)
        data = {'status': self._is_opened, 'turnamnent': str(self._turnament)}
        logging.info('Content data: \n{}'.format(data))
        return data


    def app_info(self):
        log_method(obj=self, func=self.app_info)
        data = {'name': Resources.APPLICATION_NAME, 'version': Resources.__version__}
        logging.info('Content data: \n{}'.format(data))
        return data


    def open(self, name: str, cmd: str):
        log_method(obj=self, func=self.open)
        if name:
            self._browser.set_file(path="C:", filename=name)
            self._browser.get_file(option=cmd)
            self._turnament = Turnament(name=name)
            self._is_opened = True
        data = {'status': self._is_opened, 'turnamnent': str(self._turnament)}
        logging.info('Content data: \n{}'.format(data))
        return data


    def close(self):
        log_method(obj=self, func=self.close)
        self._browser.stop()
        self._turnament.delete_players()
        self._is_opened = False


    def end(self):
        log_method(obj=self, func=self.end)
        self._end = True


    def turnament_start(self, system_type: str, rounds=0):
        if system_type.lower() in "swiss":
            if rounds == 0:
                logging.error("Set number of rounds to play!")
                return
            s_type = Resources.SystemType.SWISS
        elif system_type.lower() in "circullar":
            s_type = Resources.SystemType.CIRCULAR
            rounds = self._turnament.players_num - 1
        elif system_type.lower() in "elimination":
            s_type = Resources.SystemType.SINGLE_ELIMINATION
        else:
            logging.error("Wrong turnament system typed! {}".format(system_type))
            return
        self._turnament.set_system(system_id=s_type)
        self._turnament.begin(rounds=rounds)
        data = {'status': True, 'turnamnent': self._turnament.get()}
        logging.info('Content data: \n{}'.format(data))
        return data


    def player_add(self,
                   name="",
                   surname="",
                   sex="male",
                   city="",
                   category="bk",
                   elo=0):
        log_method(obj=self, func=self.player_add)
        if not self._turnament:
            logging.error("No turnament active. Please start turnament.")
            data = {'status': False, 'player': None}
        else:
            self._turnament.add_player(name=name,
                                       surname=surname,
                                       sex=sex,
                                       city=city,
                                       category=category,
                                       elo=elo)
            data = {'status': True, 'player': str(self._turnament._players[-1])}
        logging.info('Content data: \n{}'.format(data))
        return data


    def player_del(self,
                   name="",
                   surname=""):
        log_method(obj=self, func=self.player_del)
        if not self._turnament:
            logging.error("No turnament active. Please start turnament.")
            data = {'status': False}
        else:
            self._turnament.del_player(name=name, surname=surname)
            data = {'status': True}
        logging.info('Content data: \n{}'.format(data))
        return data


    def players_get(self,
                    type="results"):
        log_method(obj=self, func=self.players_get)
        if not self._turnament:
            logging.error("No turnament active. Please start turnament and add Players.")
            data = {'status': False, 'players': None}
        else:
            data = {'status': True, 'players': str(self._turnament.get_players(type=type))}
        logging.info('Content data: \n{}'.format(data))
        return data


    def turnament_results(self):
        log_method(obj=self, func=self.players_get)
        if not self._turnament:
            logging.error("No turnament active. Please start turnament and add Players.")
            data = {'status': False, 'round': None, 'players': None}
        else:
            data = {'status': True,
                    'round': self._turnament._act_round_nr,
                    'players': self.players_get(type='results')['players']}
        logging.info('Content data: \n{}'.format(data))
        return data


    def turnament_round(self, nr=-1):
        log_method(obj=self, func=self.turnament_tables)
        if not self._turnament:
            logging.error("No turnament active. Please start turnament with Players.")
            data = {'status': False, 'round': None}
        elif nr == -1 or nr in range(len(self._turnament._rounds)):
            data = {'status': True, 'round': self._turnament._rounds[nr].get()}
        logging.info('Content data: \n{}'.format(data))
        return data
            


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
        self._turnament.set_system(system_id=Resources.SystemType.SWISS)
        self._turnament.begin(rounds=6)
        self._turnament.add_result(table_nr=1, result=1.0)
        self._turnament.add_result(table_nr=2, result=1.0)
        self._turnament.add_result(table_nr=3, result=0.5)
        self._turnament.apply_round_results()
        logging.debug(msg=self._turnament.dump_act_results())
        # logging.debug(msg=self._turnament.dump_players())

        msg_debug = "ROUND #2:"
        logging.debug(msg=msg_debug)
        self._turnament.next_round()
        # logging.debug(msg=self._turnament.dump())
        self._turnament.add_result(table_nr=1, result=0.5)
        self._turnament.add_result(table_nr=2, result=0.0)
        self._turnament.add_result(table_nr=3, result=1.0)
        self._turnament.apply_round_results()
        logging.debug(msg=self._turnament.dump_act_results())
        # logging.debug(msg=self._turnament.dump_players())

        msg_debug = "ROUND #3:"
        logging.debug(msg=msg_debug)
        self._turnament.next_round()
        # logging.debug(msg=self._turnament.dump())
        self._turnament.add_result(table_nr=1, result=0.5)
        self._turnament.add_result(table_nr=2, result=0.0)
        self._turnament.add_result(table_nr=3, result=1.0)
        self._turnament.apply_round_results()
        logging.debug(msg=self._turnament.dump_act_results())
        # logging.debug(msg=self._turnament.dump_players())

        msg_debug = "ROUND #4:"
        logging.debug(msg=msg_debug)
        self._turnament.next_round()
        # logging.debug(msg=self._turnament.dump())
        self._turnament.add_result(table_nr=1, result=0.5)
        self._turnament.add_result(table_nr=2, result=0.5)
        self._turnament.add_result(table_nr=3, result=1.0)
        self._turnament.apply_round_results()
        logging.debug(msg=self._turnament.dump_act_results())
        # # logging.debug(msg=self._turnament.dump_players())

        msg_debug = "ROUND #5:"
        logging.debug(msg=msg_debug)
        self._turnament.next_round()
        # logging.debug(msg=self._turnament.dump())
        self._turnament.add_result(table_nr=1, result=0.5)
        self._turnament.add_result(table_nr=2, result=0.0)
        self._turnament.add_result(table_nr=3, result=1.0)
        self._turnament.apply_round_results()
        logging.debug(msg=self._turnament.dump_act_results())
        # logging.debug(msg=self._turnament.dump_players_p_o())

        msg_debug = "ROUND #6:"
        logging.debug(msg=msg_debug)
        self._turnament.next_round()
        # logging.debug(msg=self._turnament.dump())
        self._turnament.add_result(table_nr=1, result=0.5)
        self._turnament.add_result(table_nr=2, result=0.0)
        self._turnament.add_result(table_nr=3, result=0.0)
        self._turnament.apply_round_results()
        logging.debug(msg=self._turnament.dump_act_results())
        # # logging.debug(msg=self._turnament.dump_players())
