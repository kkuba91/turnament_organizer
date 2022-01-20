"""table.py

    Chess table class. First player plays whites,
    second player plays blacks. Result of table as
    for player which plays whites.

"""


class Table(object):
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
        if self.result == -1.0:
            return '--/--'
        elif self.result == 0.0:
            return '0.0/1.0'
        elif self.result == 0.5:
            return '0.5/0.5'
        elif self.result == 1.0:
            return '1.0/0.0'
    
    def dump(self):
        _str = f' Table: #{self.number}  --  result: {self._dump_result()}\n'
        _str += f'  Whites: #{self.w_player}\n'
        _str += f'  Blacks: #{self.b_player}\n'
        return _str