"""command.py

    Command API class.

"""


class Command(object):
    def __init__(self) -> None:
        self._cmd_msg = ""
        self._params = list()

    def input_std(self):
        self._cmd_msg = ""
        self._params = list()
        msg = input()
        self._interpret(msg)

    def input_set(self, msg):
        self._interpret(msg)

    def _interpret(self, msg):
        if isinstance(msg, str):
            self._cmd_msg = msg.split(" ")[0]
            msg_len = len(msg.split(" "))
            if msg_len > 1:
                params = list()
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
        if len(self._params) > 0:
            return True
        else:
            print("Wrong parameters. ")
            return False
