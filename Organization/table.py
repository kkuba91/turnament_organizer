"""table.py

    Chess table class. First player plays whites,
    second player plays blacks. Result of table as
    for player which plays whites.

"""


class Table(object):

    """Table with chessboard score class."""

    def __init__(self, nr, nr_w, nr_b):
        self.number = nr
        self.w_player = nr_w
        self.b_player = nr_b
        self.result = -1.0

    def set_result(self, result):
        if result in (0.0, 0.5, 1.0):
            self.result = result

    def set_white_player(self, nr_w):
        self.w_player = nr_w

    def set_black_player(self, nr_b):
        self.w_player = nr_b

    def swap_players(self):
        nr_w = self.w_player
        self.w_player = self.b_player
        self.b_player = nr_w

    def _dump_result(self):
        _str = "No results"
        if self.result == -1.0:
            _str = "--/--"
        elif self.result == 0.0:
            _str = "0.0/1.0"
        elif self.result == 0.5:
            _str = "0.5/0.5"
        elif self.result == 1.0:
            _str = "1.0/0.0"
        return _str

    def dump(self):
        _str = f" Table: #{self.number}  --  result: {self._dump_result()}\n"
        _str += f"  #{self.w_player} vs. #{self.b_player}"
        return _str
