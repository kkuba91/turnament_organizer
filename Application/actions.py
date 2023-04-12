"""actions.py

    Application action class with actions over the app instance
    i.e. open, close, add player, modify, ...

    @WARNING:
    Actions have one instance only over the app (singleton).

"""
# noqa: F401
# Global package imports:
import logging
from functools import cache
from tabulate import tabulate

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

    def debug_method(self):
        """Debugging purpose only.
           This example holds simple swiss system simulation (one manual test case), but critical.
           There are 6 rounds for 7 Players.
           Remarks:
            - Swiss system transform into circular.
            - Pause must be every round counted.
        """
        log_method(obj=self, func=self.debug_method)
        if self._turnament:
            self._turnament.add_player(
                name="Jacob",
                surname="K",
                sex="male",
                city="Bedzin",
                category="III",
                elo=0,
            )
            self._turnament.add_player(
                name="Joannah",
                surname="K",
                sex="female",
                city="Bedzin",
                category="bk",
                elo=0,
            )
            self._turnament.add_player(
                name="Jaroslaw",
                surname="Katchynsky",
                sex="male",
                city="Nowogrodzka",
                category="bk",
                elo=0,
            )
            self._turnament.add_player(
                name="Mateush",
                surname="Morawitz",
                sex="male",
                city="Warsaw",
                category="IV",
                elo=0,
            )
            self._turnament.add_player(
                name="Adam",
                surname="Malysh",
                sex="male",
                city="Wisla",
                category="II",
                elo=1755,
            )
            self._turnament.add_player(
                name="Piotr",
                surname="Zyla",
                sex="male",
                city="Zakopane",
                category="V",
                elo=0,
            )
            self._turnament.add_player(
                name="Mario",
                surname="Super",
                sex="male",
                city="Pilsudsky Square",
                category="bk",
                elo=1355,
            )
            msg_debug = "ROUND #1:"
            logging.debug(msg=msg_debug)
            self._turnament.set_system(system_id=1)
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
        else:
            msg_info = "No turnament file selected."
            logging.info(msg=msg_info)