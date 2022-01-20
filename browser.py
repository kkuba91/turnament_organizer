import errno, os
from os import system as sys

"""browser.py

    Browser class with with additional File class.

"""

class File(object):
    def __init__(self) -> None:
        self._name = ""
        self._path = ""
        self._valid = False
    
    def init(self):
        self._name = ""
        self._path = ""
        self._valid = False
    
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
            print('File verification failed.')
            print(self)
        return self._valid
    
    def _is_name_valid(self) -> bool:
        _valid = False
        if isinstance(self._name, str):
            if self._name.isalpha():
                 _valid = True
            else:
                print('Wrong filename.. ')
        return _valid
            
    def _is_path_valid(self) -> bool:
        try:
            if not isinstance(self._path, str) or not self._path:
                print('Wrong path type.. ')
                return False

            _, self._path = os.path.splitdrive(self._path)

            root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
                # if sys.platform == 'win32' else os.path.sep
            assert os.path.isdir(root_dirname)

            root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

            for pathname_part in self._path.split(os.path.sep):
                try:
                    os.lstat(root_dirname + pathname_part)
                except OSError as exc:
                    if hasattr(exc, 'winerror'):
                        if exc.winerror == 123:
                            print('Wrong path with  winerror 123.. ')
                            return False
                    elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                        print('Wrong path.. ')
                        return False
        except TypeError as exc:
            print('Wrong path type.. ')
            return False
        else:
            return True

    def __repr__(self):
        return str(f'File object of {self._name} inside dirctory {self._path} .')

class Browser(object):
    def __init__(self) -> None:
        self._file_opened = False
        self._option = ""
        self._success = False
        self._file = File()
        self._file_handler: None
    
    def set_file(self, path, filename) -> bool:
        if not self.is_file_opened():
            self._file.set_path(path).set_name(filename)
            return self._file.verify()
        else:
            return False
        
            
    def get_file(self, option):
        _log = ""
        if self._file._valid:
            self._option = option
            for self._option in ['Open', 'New']:   
                if option == 'New':
                    self._success = self._create_file()
                    _log = f'Opened new db "{self._file._name}". '
                elif option == 'Open':
                    self._success = self._get_file()
                    _log = f'Opened existing db "{self._file._name}". '
                if self._success and option:
                    self._file_opened = True
                    print(_log)
                return self._file_handler
            else:
                return None
        else:
            self._option = ""
            print('Wrong file coordinates.')
            return None
    
    def stop(self):
        self._option = ""
        _log = f'Closed db "{self._file._name}". '
        if self._file_opened:
            self._file_handler.close()
            self._file_opened = False
            self._file.init()
            print(_log)
        else:
            print('Browser already closed.')
        return self._success
    
    def is_file_opened(self):
        return self._file_opened

    def _create_file(self):
        _success = False
        _full_file_name = self._file._path + '\\' + self._file._name + '.dbc'
        try:
            self._file_handler = open(_full_file_name, 'w+')
            _success = True
        except Exception:
            print(f'Failed to create new file {_full_file_name}..')
            _success = False
        return _success

    def _get_file(self):
        _success = False
        _full_file_name = self._file._path + '\\' + self._file._name + '.dbc'
        try:
            self._file_handler = open(_full_file_name, 'r+')
            _success = True
        except Exception:
            print(f'Failed to create new file "{_full_file_name}"..')
            _success = False
        return _success

    
if __name__=="__main__":
    _comment = 'Browser class for creating new Turnament DB or opening existing one.'
    print(_comment)