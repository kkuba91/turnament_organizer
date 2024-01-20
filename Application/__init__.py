"""__init__.py

    Application class with initailization, run and ending.
    Than layer suppose to handle main app machine state decisions.

"""
# noqa: F401
# Global package imports:
import logging

# Local package imports:
from Application.actions import Actions
from Application.Interfaces.api import ApiData
from Application.Interfaces.Command.cli import CLI
from Application.logger import set_logging

# Third party packages:
from Resources import __version__

DEBUG = True


class Application:
    def __init__(self, name):
        self._logger = set_logging(debug=DEBUG)
        self._name = name
        self._end = False
        msg = f'Starting "{name}" application (ver {__version__}).. '
        logging.info(msg)
        self.actions = Actions(name=name)

    def init(self):
        self.cli = CLI(app=self)
        self.api = ApiData(app=self, logger=self._logger)

    def run(self):
        self._run_api()
        self._run_cli()
    
    def end(self):
        self._end = True

    def _run_cli(self):
        self.cli.run_cli()

    def _run_api(self):
        self.api.run_api()


if __name__ == "__main__":
    msg_comment = "Application class. It handles init(), run() and end() methods. "
    logging.info(msg=msg_comment)
