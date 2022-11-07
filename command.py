"""command.py

    Commandline API class.

"""
import logging


class Command:

    """Commandline class handler."""

    def __init__(self) -> None:
        self._cmd_msg = ""
        self._params = []

    def input_std(self):
        self._cmd_msg = ""
        self._params = []
        try:
            msg = input()
        except KeyboardInterrupt:
            msg_debug = "Keyboard interrupt detected. App closed."
            logging.debug(msg=msg_debug)
            msg = "End"
        self._interpret(msg)

    def input_set(self, msg):
        self._interpret(msg)

    def _interpret(self, msg):
        if isinstance(msg, str):
            self._cmd_msg = msg.split(" ")[0]
            msg_len = len(msg.split(" "))
            if msg_len > 1:
                params = []
                params = msg.split(" ")[1:msg_len]
                self._params = params

    def get_param(self, ident):
        return self._params[ident]

    def get_cmd(self):
        return self._cmd_msg

    def check_param(self, ident, param):
        return self._params[ident] == param

    def check_cmd(self, cmd_msg):
        return self._cmd_msg == cmd_msg

    def is_params(self):
        _result = False
        if len(self._params) > 0:
            _result = True
        else:
            msg_info = "Wrong/no parameters. "
            logging.info(msg=msg_info)
        return _result
