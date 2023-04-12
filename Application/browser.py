"""browser.py

    Browser class with with additional File class.

"""
import os
import errno
import logging


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
            if self._name.isalpha():
                _valid = True
            else:
                msg_error = "Wrong filename.. "
                logging.error(msg=msg_error)
        return _valid

    def _is_path_valid(self) -> bool:
        try:
            if not isinstance(self._path, str) or not self._path:
                msg_error = "Wrong path type.. "
                logging.error(msg=msg_error)
                return False

            _, self._path = os.path.splitdrive(self._path)

            root_dirname = os.environ.get("HOMEDRIVE", "C:")
            assert os.path.isdir(root_dirname)

            root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

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
        return str(f"File object of {self._name} inside dirctory {self._path} .")


class Browser(object):
    def __init__(self) -> None:
        self._file_opened = False
        self._option = ""
        self._success = False
        self._file = File()
        self._file_handler = None

    def set_file(self, path, filename) -> bool:
        if not self.is_file_opened():
            self._file.set_path(path).set_name(filename)
            return self._file.verify()
        else:
            return False

    def get_file(self, option):
        _log = ""
        _ret = None
        if self._file.valid:
            self._option = option
            if self._option in ("Open", "New"):
                if option == "New":
                    self._success = self._create_file()
                    _log = f'Opened new db "{self._file.name}". '
                elif option == "Open":
                    self._success = self._get_file()
                    _log = f'Opened existing db "{self._file.name}". '
                if self._success and option:
                    self._file_opened = True
                    logging.info(msg=_log)
                _ret = self._file_handler
        else:
            self._option = ""
            msg_error = "Wrong file coordinates."
            logging.error(msg=msg_error)
        return _ret

    def stop(self):
        self._option = ""
        _log = f'Closed db "{self._file.name}". '
        if self._file_opened:
            self._file_handler.close()
            self._file_opened = False
            self._file.init()
            logging.info(msg=_log)
        else:
            msg_error = "Browser already closed."
            logging.error(msg=msg_error)
        return self._success

    def is_file_opened(self):
        return self._file_opened

    def _create_file(self):
        _success = False
        _full_file_name = self._file.path + "\\" + self._file.name + ".dbc"
        try:
            self._file_handler = open(_full_file_name, "w+", encoding="utf-8")
            _success = True
        except (FileExistsError, PermissionError, FileNotFoundError) as exc:
            msg_error = f"Failed to create new file {_full_file_name}.. ({str(exc)}) "
            logging.error(msg=msg_error)
            _success = False
        return _success

    def _get_file(self):
        _success = False
        _full_file_name = self._file.path + "\\" + self._file.name + ".dbc"
        try:
            self._file_handler = open(_full_file_name, "r+", encoding="utf-8")
            _success = True
        except (FileExistsError, PermissionError, FileNotFoundError) as exc:
            msg_error = f"Failed to create/open the file {_full_file_name}.. ({str(exc)}) "
            logging.error(msg=msg_error)
            _success = False
        return _success


if __name__ == "__main__":
    msg_comment = "Browser class for creating new Turnament DB or opening existing one."
    logging.info(msg=msg_comment)
