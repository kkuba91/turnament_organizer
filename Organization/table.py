"""table.py

    Chess table class. First player plays whites,
    second player plays blacks. Result of table as
    for player which plays whites.

"""
# Global package imports:

# Local package imports:
from Organization.Models import ModelTable


class Table(ModelTable):

    """Table with chessboard score class."""

    def set_result(self, result):
        if result in (0.0, 0.5, 1.0):
            self.result = result

    def set_white_player(self, id_w):
        self.w_player.id = id_w

    def set_black_player(self, id_b):
        self.w_player.id = id_b

    def swap_players(self):
        buffer_w = self.w_player
        self.w_player = self.b_player
        self.b_player = buffer_w

    def is_pauser(self):
        return self.w_player.id == -1 or self.b_player.id == -1

    def _dump_result(self):
        _str = "No results"
        if self.result == -1.0:
            _str = "---/---"
        elif self.result == 0.0:
            _str = "0.0/1.0"
        elif self.result == 0.5:
            _str = "0.5/0.5"
        elif self.result == 1.0:
            _str = "1.0/0.0"
        return _str

    def get(self, full=True, specific=[]):
        if full:
            return {
                'nr': self.number,
                'white': self.w_player.get(specific=specific),
                'black': self.b_player.get(specific=specific),
                'result': self._dump_result()
            }
        else:
            return {
                'nr': self.number,
                'white': self.w_player.get_repr(),
                'black': self.b_player.get_repr(),
                'result': self._dump_result()
            }

    def dump(self):
        _str = f"Table: #{self.number}  --  result: {self._dump_result()}"
        _str += f"  #{self.w_player} vs. #{self.b_player}"
        return _str

    def dump_with_no_results(self):
        _str = ""
        if self.result == -1.0:
            _str = f"Table: #{self.number}  --  result: {self._dump_result()}"
            _str += f"  #{self.w_player} vs. #{self.b_player} \n"
        return _str
