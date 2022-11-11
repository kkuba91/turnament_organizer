"""round.py

    Turnament round with all data about playing sets and resuts.

"""
from Organization.table import Table
from Organization.Models import ModelRound


class Round(ModelRound):
    """Turnament round class."""

    def add_table(self, player_w, player_b):
        next_nr = len(self.tables) + 1
        table = Table(
            nr=next_nr,
            w_player=player_w,
            b_player=player_b
            )
        self.tables[next_nr] = table
        return next_nr

    def set_result(self, table_nr, result):
        self.tables[table_nr].result = result
        self.all_results = self._check_results()

    def _check_results(self):
        all_results = True
        for _, table in self.tables.items():
            if table.result == -1.0:
                all_results = False
        return all_results

    def get_opponent(self, _idnt):
        _ret = None
        for _, table in self.tables.items():
            if table.w_player == _idnt:
                _ret = table.b_player
            if table.b_player == _idnt:
                _ret = table.w_player
        return _ret

    def change_player(self, player_old, player_new):
        _n_replaced = True
        for _, table in self.tables.items():
            if _n_replaced:
                if table.w_player == player_old:
                    table.w_player = player_new
                    _n_replaced = False
                if table.b_player == player_old:
                    table.b_player = player_new
                    _n_replaced = False

    def dump(self):
        _str = f"Round nr: {self.number}\n"
        for table_nr in range(1, len(self.tables) + 1):
            _str += self.tables[table_nr].dump_with_no_results()
        if self.pausing > 0:
            _str += f"Player with a Pause: #{self.pausing}\n"
        return _str
