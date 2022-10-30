"""round.py

    Turnament round with all data about playing sets and resuts.

"""
from Organization.table import Table


class Round(object):
    def __init__(self) -> None:
        self.number = 0
        self.tables = dict()
        self.pausing = 0
        self.all_results = False
        self._players_num = 0
        self._tables_num = 0

    def add_table(self, player_w, player_b):
        next_nr = len(self.tables) + 1
        table = Table(next_nr, player_w, player_b)
        self.tables[next_nr] = table
        return next_nr

    def set_result(self, table_nr, result):
        self.tables[table_nr].result = result
        self.all_results = self._check_results()

    def _check_results(self):
        all_results = True
        for table in self.tables:
            if table.result == -1.0:
                all_results = False
        return all_results

    def get_opponent(self, _idnt):
        _ret = None
        for nr in self.tables:
            if self.tables[nr].w_player == _idnt:
                _ret = self.tables[nr].b_player
            if self.tables[nr].b_player == _idnt:
                _ret = self.tables[nr].w_player
        return _ret

    def change_player(self, player_old, player_new):
        _n_replaced = True
        for nr in self.tables:
            if _n_replaced:
                if self.tables[nr].w_player == player_old:
                    self.tables[nr].w_player = player_new
                    _n_replaced = False
                if self.tables[nr].b_player == player_old:
                    self.tables[nr].b_player = player_new
                    _n_replaced = False

    def dump(self):
        _str = f"Round nr: {self.number}\n"
        for nr in range(1, len(self.tables) + 1):
            _str += self.tables[nr].dump()
        if self.pausing > 0:
            _str += f"Player with a Pause: #{self.pausing}\n"
        return _str
