# Local package imports:
from Application.logger import debug
from Application.Interfaces.Command import Command


class CLI:

    """Commandline communication interface methods."""

    def __init__(self, **kwargs) -> None:
        self._cmd = Command()
        self.app = kwargs.get('app')
        self._end = False
        if not isinstance(self.app, object):
            raise TypeError("No APP object for CLI.")
        self.methods = [method for method in dir(self.__class__) if method.startswith('dir_') is True]

    def _choice(self, method="cmd", cmd=""):
        if method == "cmd":
            self._cmd.input_std()
        else:
            self._cmd.input_set(cmd)
    
    def dir_help(self):
        if self._cmd.check_cmd("help"):
            print("SELECT ONE OF: New, Open, Close, End")

    def dir_open(self):
        if self._cmd.check_cmd("Open") or self._cmd.check_cmd("New"):
            if self._cmd.is_params():
                self.app.actions.open(name=self._cmd.get_param(0), cmd=self._cmd.get_cmd())
    
    def dir_end(self):
        if self._cmd.check_cmd("End"):
            self._end = True
            self.app.actions.end()
    
    def dir_close(self):
        if self._cmd.check_cmd("Close"):
            self.app.actions.close()
    
    @debug
    def dir_debug(self):
        """Debugging purpose only.
        """
        if self._cmd.check_cmd("debug"):
           self.app.actions.debug_method()

    def run_cli(self):
        """Simple CLI for calling 'dir_.. methods.
        """
        while not self._end:
            self._choice(method="cmd")
            for method in self.methods:
                self.__getattribute__(method)()
