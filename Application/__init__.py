"""__init__.py

    Application class with initailization, run and ending.
    Than layer suppose to handle main app machine state decisions.

"""
# noqa: F401
# Global package imports:
import argparse
import logging
import platform
import webbrowser

# Local package imports:
from Application.actions import Actions
from Application.Interfaces.api import ApiData
from Application.Interfaces.Command.cli import CLI
from Application.logger import set_logging
from Resources import __version__

# Third party packages:


class ArgInfo:
    def __init__(self, default_port: int, default_debug: bool, app_name: str) -> None:
        self._cmd_start = "py" if "win" in platform.system().lower() else "python3"
        self._parser = argparse.ArgumentParser(
            prog=f'{app_name} v{__version__}',
            description='Fast pairing program to manage chess tournaments.',
            epilog=f'To start, type: "{self._cmd_start} runner.py".'
                   f'For more detailed help, type: "{self._cmd_start} runner.py -h"')
        self._parser.add_argument('-p', '--port', default=default_port, type=int, help=f"service port run on localhost (by default port={default_port})")
        self._parser.add_argument('--debug', action='store_true', help=f"run logging in debug level (by default debug={default_debug})")
        args = self._parser.parse_args()
        self.port = args.port
        self.debug = args.debug or default_debug


class Application:
    def __init__(self, name, port, debug=False):
        self._logger = set_logging(debug=debug)
        self._name = name
        self._port = port
        self._end = False
        msg = f'Starting "{name}" application (ver {__version__}).. '
        logging.info(msg)
        self.actions = Actions(name=name)

    def init(self):
        self.cli = CLI(app=self)
        self.api = ApiData(app=self, logger=self._logger, port=self._port)

    def run(self):
        webbrowser.open(f"http://127.0.0.1:{self._port}/")
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
