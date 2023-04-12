"""player.py

    Chess player class. All data related to Player,
    which can b set at the begining and during the game.

"""
# Global package imports:
import logging
from datetime import date

# Local package imports:
from Organization.Models import ModelPlayer
from Resources import CATEGORY


class Player(ModelPlayer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        pauser = kwargs.get('pauser')
        if pauser:
            attr_val = kwargs.get('pauser')
            if isinstance(attr_val, bool):
                self.pauser = attr_val
            else:
                self.pauser = bool(attr_val)
        if self.pauser:
            self.id = -1
            self.rank = 0
            self.elo = 0
            self.category = "bk"
            self.name = ' -- '
            self.surname = ' -- '
        else:
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
            try:
                self.rank = CATEGORY[self.sex][self.category]
            except KeyError as exc:
                logging.error("{}, forkeys: sex='{}', category='{}'".format(exc, self.sex, self.category))
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
        # self.possible_opponents = [opponent for opponent in players if (opponent.id not in self.opponents) and (opponent not in self.possible_opponents) and (self.id != opponent.id)]
        for player in players:
            if self.pauser:
                if not player.paused and player.id != self.id:
                    self.possible_opponents.append(player)
            else:
                if player.id != self.id and player.id not in self.opponents:
                    self.possible_opponents.append(player)
        # if self.paused:
        #     self.possible_opponents.append(-1)
        

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
