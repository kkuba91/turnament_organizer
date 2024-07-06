"""browser.py

    Browser class with additional File class.

"""
import shutil
import os
import errno
import logging
import sys

from sqlalchemy import create_engine


class File(object):
    def __init__(self) -> None:
        self._name = ""
        self._path = ""
        self._valid = False

    def init(self):
        self._name = ""
        self._path = ""
        self._valid = False

    @property
    def valid(self):
        return self._valid

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    def set_name(self, name):
        self._name = str(name)
        return self

    def set_path(self, path):
        self._path = str(path)
        return self

    def verify(self) -> bool:
        if self._is_name_valid():
            if self._is_path_valid():
                self._valid = True
        if not self._valid:
            msg_error = "File verification failed."
            logging.error(msg=msg_error)
            msg_error = str(self)
            logging.error(msg=msg_error)
        return self._valid

    def _is_name_valid(self) -> bool:
        _valid = False
        if isinstance(self._name, str):
            if self._name.replace("_", "").isalnum():
                _valid = True
            else:
                msg_error = f"Wrong filename.. ({self._name})"
                logging.error(msg=msg_error)
        return _valid

    def _is_path_valid(self) -> bool:
        try:
            if not isinstance(self._path, str) or not self._path:
                msg_error = f"Wrong path type.. ({self._path})"
                logging.error(msg=msg_error)
                return False

            _, self._path = os.path.splitdrive(self._path)

            root_dirname = os.environ.get("HOMEDRIVE", "C:") if "win" in sys.platform \
                else ""

            root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep
            logging.debug(f"is_path_valid - root_dirname: {self._path}")

            for pathname_part in self._path.split(os.path.sep):
                try:
                    os.lstat(root_dirname + pathname_part)
                except OSError as exc:
                    if hasattr(exc, "winerror"):
                        if exc.winerror == 123:
                            msg_error = f"Wrong path with  winerror.. ({str(exc)}) "
                            logging.error(msg=msg_error)
                            return False
                    elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                        msg_error = "Wrong path.. "
                        logging.error(msg=msg_error)
                        return False
        except TypeError as exc:
            msg_error = f"Wrong path type.. ({str(exc)}) "
            logging.error(msg=msg_error)
            return False
        else:
            return True

    def __repr__(self):
        return str(f"File object of {self._name} inside directory {self._path} .")


class Browser(object):
    def __init__(self) -> None:
        logging.getLogger("uvicorn")
        self.dir_path = ""
        self.filename = ""
        self._file_opened = False
        self._option = ""
        self._success = False
        self._file = File()
        self._file_handler = None
        self.engine = None

    def set_file(self, filename, path="") -> bool:
        if not path:
            path = os.path.expanduser('~') + os.sep + ".turnament_organizer" + os.sep + filename
        logging.debug(f"set_file path: {path}, with filename: {filename}")
        self.dir_path = path
        self.filename = filename
        if not self.is_file_opened():
            self._file.set_path(path).set_name(filename)
            return self._file.verify()
        else:
            return False

    def remove_tournament_from_list(self, tournament_name, path=""):
        if tournament_name:
            if not path:
                path = os.path.expanduser('~') + os.sep + ".turnament_organizer" + os.sep + tournament_name
            print(f"tournament_name={tournament_name}, path={path}")
            if os.path.exists(path=path):
                logging.debug(f"Remove tournament '{tournament_name}' files in path={path}")
                try:
                    shutil.rmtree(path=path)
                except Exception as exc:
                    logging.error(f"Cannot remove files in {path}, because of error: {exc}")
                else:
                    return True

    def get_file(self, option, path=""):
        _log = ""
        _ret = None
        if self._file.valid:
            self._option = option
            if self._option in ("Open", "New"):
                if option == "New":
                    self._success = self._create_file(path=path)
                    _log = f'Opened new db "{self._file.name}". '
                elif option == "Open":
                    self._success = self._get_file()
                    _log = f'Opened existing db "{self._file.name}". '
                if self._success and option:
                    self._file_opened = True
                    logging.info(msg=_log)
        else:
            self._option = ""
            msg_error = "Wrong file coordinates."
            logging.error(msg=msg_error)
        return _ret

    def stop(self):
        self._option = ""
        _log = f'Closed db "{self._file.name}". '
        if self._file_opened:
            # self._file_handler.close()
            self._file_opened = False
            self._file.init()
            logging.info(msg=_log)
        else:
            msg_error = "Browser already closed."
            logging.error(msg=msg_error)
        return self._success

    def is_file_opened(self):
        return self._file_opened

    def get_file_list(self, path="") -> list:
        _user_path = self._get_user_path(path=path)
        return [d for d in os.listdir(_user_path) if os.path.isdir(os.path.join(_user_path, d))]

    def _create_file(self, path=""):
        _success = False
        _user_path = self._get_user_path(path=path)
        _full_file_name = _user_path + os.path.sep + self._file.name + ".db"
        logging.debug(f"Trying to create turnament db file: {_full_file_name}")
        try:
            if not os.path.isfile(_full_file_name):
                self._file_handler = open(_full_file_name, "w+", encoding="utf-8")
                self._file_handler.close()
            _success = os.path.isfile(_full_file_name)
        except (FileExistsError, PermissionError, FileNotFoundError) as exc:
            msg_error = f"Failed to create new file {_full_file_name}.. ({str(exc)}) "
            logging.error(msg=msg_error)
            _success = False

        if _success:
            self.engine = create_engine(f'sqlite:///{_full_file_name}',
                                        echo=False,
                                        echo_pool=False)
            self.engine.connect()
            logging.debug(f"Connected to db file: {self.engine.url}")
        return _success

    def add_or_update_extra_file(self, filename, content):
        _user_path = self._get_user_path()
        _full_file_name = _user_path + os.path.sep + filename
        with open(_full_file_name, "w+", encoding="utf-8") as file_handler:
            file_handler.write(content)
        return (_full_file_name, filename) if os.path.isfile(_full_file_name) else ("", "")

    def _get_user_path(self, path=""):
        _user_path = os.path.expanduser('~') if "/root" != os.path.expanduser('~') else ""
        _user_path += os.path.sep + path if path else os.path.sep + ".turnament_organizer" + os.path.sep + self._file.name
        if not os.path.exists(_user_path):
            logging.debug(f"Dir: {_user_path} does not exist.. make a dir..")
            os.makedirs(_user_path)
        return _user_path

    def _get_file(self):
        _success = False
        _full_file_name = self._file.path + os.path.sep + self._file.name + ".db"
        try:
            _success = True
        except (FileExistsError, PermissionError, FileNotFoundError) as exc:
            msg_error = f"Failed to create/open the file {_full_file_name}.. ({str(exc)}) "
            logging.error(msg=msg_error)
            _success = False
        return _success


if __name__ == "__main__":
    msg_comment = "Browser class for creating new Turnament DB or opening existing one."
    logging.info(msg=msg_comment)
