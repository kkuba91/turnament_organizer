"""application.py

    Application class with initailization, run and ending.

"""
# Global package imports:
import os
import logging

# Local package imports:
from browser import Browser
from command import Command
from turnament import Turnament


DEBUG = True


def debug(func):
    """Debug filtered action - @decorator."""

    def function_handler(*args, **kvargs):
        _ret = None
        if DEBUG:
            _ret = func(*args, **kvargs)
        return _ret

    return function_handler


def set_logging() -> None:
    """Set logging configuration."""
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
        msg_debug = "Debugging is switched ON!"
        logging.debug(msg=msg_debug)
    else:
        logging.basicConfig(level=logging.INFO)


class Application:
    def __init__(self, name):
        set_logging()
        self._name = name
        self._end = False
        self._is_db_opened = False
        self._is_browser_opened = False
        self._browser: None
        self._cmd: None
        self._turnament: None
        msg = f'Starting "{name}" application.. '
        logging.info(msg)

    def init(self):
        self._browser = Browser()
        self._cmd = Command()

    def run(self):
        while not self._end:
            self.choice(method="cmd")
            self.dir_help()
            self.dir_new()
            self.dir_open()
            self.dir_close()
            self.dir_end()
            self.dir_debug()

    def end(self):
        pass

    def choice(self, method="cmd", cmd=""):
        if method == "cmd":
            self._cmd.input_std()
        else:
            self._cmd.input_set(cmd)

    def dir_help(self):
        if self._cmd.check_cmd("help"):
            print("SELECT ONE OF: New, Open, Close, End")

    def dir_new(self):
        if self._cmd.check_cmd("New"):
            if self._cmd.is_params():
                self._browser.set_file(path="C:", filename=self._cmd.get_param(0))
                self._browser.get_file(option=self._cmd.get_cmd())
                self._turnament = Turnament(name=self._cmd.get_param(0))

    def dir_open(self):
        if self._cmd.check_cmd("Open"):
            if self._cmd.is_params():
                self._browser.set_file(path="C:", filename=self._cmd.get_param(0))
                self._browser.get_file(option=self._cmd.get_cmd())
                self._turnament = Turnament(name=self._cmd.get_param(0))

    def dir_close(self):
        if self._cmd.check_cmd("Close"):
            self._browser.stop()
            self._turnament.delete_players()

    def dir_end(self):
        if self._cmd.check_cmd("End"):
            self._end = True

    @debug
    def dir_debug(self):
        """Debugging purpose only."""
        if self._cmd.check_cmd("debug"):
            os.system("cls" if os.name == "nt" else "clear")
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
                self._turnament.begin(rounds=6)
                self._turnament.add_result(table_nr=1, result=1.0)
                self._turnament.add_result(table_nr=2, result=1.0)
                self._turnament.add_result(table_nr=3, result=0.5)
                self._turnament.apply_round_results()
                # logging.debug(msg=self._turnament.dump_act_results())
                # logging.debug(msg=self._turnament.dump_players())

                msg_debug = "ROUND #2:"
                logging.debug(msg=msg_debug)
                self._turnament.next_round()
                # logging.debug(msg=self._turnament.dump())
                self._turnament.add_result(table_nr=1, result=0.5)
                self._turnament.add_result(table_nr=2, result=0.0)
                self._turnament.add_result(table_nr=3, result=1.0)
                self._turnament.apply_round_results()
                # logging.debug(msg=self._turnament.dump_act_results())
                # logging.debug(msg=self._turnament.dump_players())

                msg_debug = "ROUND #3:"
                logging.debug(msg=msg_debug)
                self._turnament.next_round()
                # logging.debug(msg=self._turnament.dump())
                self._turnament.add_result(table_nr=1, result=0.5)
                self._turnament.add_result(table_nr=2, result=0.0)
                self._turnament.add_result(table_nr=3, result=1.0)
                self._turnament.apply_round_results()
                # logging.debug(msg=self._turnament.dump_act_results())
                # logging.debug(msg=self._turnament.dump_players())

                msg_debug = "ROUND #4:"
                logging.debug(msg=msg_debug)
                self._turnament.next_round()
                # logging.debug(msg=self._turnament.dump())
                self._turnament.add_result(table_nr=1, result=0.5)
                self._turnament.add_result(table_nr=2, result=0.5)
                self._turnament.add_result(table_nr=3, result=1.0)
                self._turnament.apply_round_results()
                # logging.debug(msg=self._turnament.dump_act_results())
                # logging.debug(msg=self._turnament.dump_players())

                msg_debug = "ROUND #5:"
                logging.debug(msg=msg_debug)
                self._turnament.next_round()
                # logging.debug(msg=self._turnament.dump())
                self._turnament.add_result(table_nr=1, result=0.5)
                self._turnament.add_result(table_nr=2, result=-1.0)
                self._turnament.add_result(table_nr=3, result=1.0)
                self._turnament.apply_round_results()
                # logging.debug(msg=self._turnament.dump_act_results())
                logging.debug(msg=self._turnament.dump_players_p_o())

                msg_debug = "ROUND #6:"
                logging.debug(msg=msg_debug)
                self._turnament.next_round()
                # logging.debug(msg=self._turnament.dump())
                self._turnament.add_result(table_nr=1, result=0.5)
                self._turnament.add_result(table_nr=2, result=0.0)
                self._turnament.add_result(table_nr=3, result=0.0)
                self._turnament.apply_round_results()
                logging.debug(msg=self._turnament.dump_act_results())
                # logging.debug(msg=self._turnament.dump_players())
            else:
                msg_info = "No turnament file selected."
                logging.info(msg=msg_info)


if __name__ == "__main__":
    msg_comment = "Application class. It handles init(), run() and end() methods. "
    logging.info(msg=msg_comment)
