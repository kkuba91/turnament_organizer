"""player.py

    Chess player class. All data related to Player,
    which can b set at the begining and during the game.

"""
# Global package imports:
from datetime import date

# Local package imports:
from Organization.Models import ModelPlayer
from resources import CATEGORY


class Player(ModelPlayer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.calculate_rank()

    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id

    def __repr__(self):
        ret = f"\n#({self.id})"
        ret += self.dump()
        return ret

    def add_opponent(self, player):
        self.opponents.append(player)

    def add_result(self, val):
        self.results.append(val)

    def get_by_ident(self, ident):
        if ident == self.id:
            return f"{self.surname} {self.name}"
        else:
            return None

    def calculate_rank(self):
        if self.elo > 0:
            self.rank = self.elo
        else:
            self.rank = CATEGORY[self.sex][self.category]
        return self

    def exist(self, name, surname):
        _exist = False
        if self.name == name and self.surname == surname:
            _exist = True
        else:
            _exist = False
        return _exist

    def set_round(self, round_nr, opponent_idnt, result=-1.0):
        while len(self.opponents) < round_nr:
            self.opponents.append(-1)
        while len(self.results) < round_nr:
            self.results.append(-1)
        self.opponents[round_nr - 1] = opponent_idnt
        self.results[round_nr - 1] = result

    def check_opponent_played(self, opponent_idnt):
        _played = False
        for opponent in self.opponents:
            if opponent == opponent_idnt and not _played:
                _played = True
        if opponent_idnt == self.id:
            _played = True
        return _played

    def refresh_possible_opponents(self, players):
        self.possible_opponents.clear()
        for player in players:
            if player.id != self.id and player.id not in self.opponents:
                self.possible_opponents.append(player.id)
        if not self.paused:
            self.possible_opponents.append(-1)

    def dump(self):
        _dump = f"\nPLAYER (#{self.id}): {self.name} {self.surname}\n"
        _dump += f"Sex: {self.sex}\n"
        # _dump += f"Birth: {self.birth_date}\n"
        _dump += f"City: {self.city}\n"
        _dump += f"Category: {self.category}\n"
        _dump += f"Elo rating: {self.elo}\n"
        _dump += f"Turnament rating: {self.rank}\n"
        return _dump

    def dump_short(self):
        _dump = f"\nPLAYER #{self.idnt}: {self.name} {self.surname}"
        return _dump

    def dump_opponents(self):
        _round_nr = 1
        _dump = "Opponents:\n"
        for oppo in self.opponents:
            _dump += (
                f"Round {_round_nr}: #{oppo}, Result: {self.results[_round_nr-1]}\n"
            )
            _round_nr += 1
        return _dump

    def dump_possible_opponents(self):
        _dump = f"Player: #{self.id} can play with:\n"
        for oppo in self.possible_opponents:
            _dump += f"{oppo}, "
        _dump += "\n"
        return _dump
