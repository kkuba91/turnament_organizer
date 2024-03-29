"""round.py

    Turnament round with all data about playing sets and results.

"""
from Organization.table import Table
from Organization.Models import ModelRound


class Round(ModelRound):
    """Turnament round class."""

    def add_table(self, player_w, player_b):
        next_nr = len(self.tables) + 1
        table = Table(
            number=next_nr,
            w_player=player_w,
            b_player=player_b
            )
        self.tables[next_nr] = table
        # Pausing option:
        if player_w.id == -1:
            self.set_result(table_nr=next_nr, result=0.0)
        elif player_b.id == -1:
            self.set_result(table_nr=next_nr, result=1.0)
        # If Previous table has Parser, swap tables (Parser table must be las one):
        if next_nr > 1:
            if self.tables[next_nr-1].w_player.id == -1 or self.tables[next_nr-1].b_player.id == -1:
                buffer_table = self.tables[next_nr-1]
                self.tables[next_nr-1] = self.tables[next_nr]
                self.tables[next_nr] = buffer_table
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

    def correct_table_order(self):
        table_pauser = None
        nr = 1
        tables = {}
        for _, table in self.tables.items():
            if table.is_pauser():
                table_pauser = table
            else:
                print(f"TABLE: {nr} - {table.w_player.id} vs {table.b_player.id}")
                tables[nr] = table
                nr += 1
        if table_pauser:
            print(f"TABLE: {nr} - {table.w_player.id} vs {table.b_player.id} (PAUSER)")
            tables[nr] = table_pauser
        self.tables = tables

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

    def get(self, full=True):
        pauser_id = -1
        data = {
            'nr': self.number,
            'tables': [],
            'pauser': self.pausing
        }
        # self.correct_table_order()
        table_nr = 1
        for _ in range(1, len(self.tables) + 1):
            specific = ["id", "name", "surname", "cat", "elo", "result"]
            table = self.tables[table_nr].get(full=full, specific=specific)
            table["nr"] = table_nr
            if pauser_id != table['white']['id'] and pauser_id != table['black']['id']:
                data['tables'].append(table)
                table_nr += 1
        return data

    def dump(self):
        _str = f"Round nr: {self.number}\n"
        for table_nr in range(1, len(self.tables) + 1):
            _str += self.tables[table_nr].dump_with_no_results()
        if self.pausing > 0:
            _str += f"Player with a Pause: #{self.pausing}\n"
        return _str
