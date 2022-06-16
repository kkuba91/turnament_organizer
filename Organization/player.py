"""player.py

    Chess player class. All data related to Player,
    which can b set at the begining and during the game.

"""
# Global package imports:
from datetime import date

# Local package imports:

CATEGORY = {
        "male":{
            "m": 2400,
            "im": 2400,
            "k++": 2300,
            "k+": 2300,
            "k": 2200,
            "I++": 2100,
            "I+": 2100,
            "I": 2000,
            "II+": 1900,
            "II": 1800,
            "III": 1600,
            "IV": 1400,
            "V": 1200,
            "bk": 1000,
            "wc": 1000
            },
        "female":{
            "m": 2200,
            "iwm": 2200,
            "k++": 2100,
            "k+": 2100,
            "k": 2000,
            "I++": 1900,
            "I+": 1900,
            "I": 1800,
            "II+": 1700,
            "II": 1600,
            "III": 1400,
            "IV": 1250,
            "V": 1100,
            "bk": 1000,
            "wc": 1000
            }
    }


class Player(object):
    def __init__(self) -> None:
        # Static Player data:
        self._name = ""
        self._surname = ""
        self._sex = ""
        self._birth_date: date
        self._city = ""
        self._category = "bk"
        self._elo = 0
        self._rank = 1000
        self._club = ""

        # Dynamic Player data:
        self._place = 0
        self._idnt = 0
        self._paused = False
        self._points = 0.0
        self._progress = 0.0
        self._bucholz = 0.0
        self._achieved_rank = 0
        self._last_played_white = False
        self._rounds = None
        self._opponents = list()
        self._possible_opponents = list()
        self._results = list()
        self._set = False    # For setting round flag
        self._round_done = False
    
    def __repr__(self):
        ret = f'\n#({self._idnt})'
        ret += self.dump()
        return ret

    def set_name(self, name):
        self._name = name
        return self
    
    def set_surname(self, surname):
        self._surname = surname
        return self
    
    def set_sex(self, sex):
        self._sex = sex
        return self
    
    def set_birthdate(self, birthdate):
        self._birth_date = birthdate
        return self
    
    def set_city(self, city):
        self._city = city
        return self
    
    def set_category(self, category):
        self._category = category
        return self
    
    def set_elo(self, elo):
        self._elo = elo
        return self

    def set_club(self, club):
        self._club = club
        return club

    def get_name(self):
        return self._name
    
    def get_surname(self):
        return self._surname
    
    def get_by_ident(self, ident):
        if ident == self._idnt:
            return f'{self._surname} {self._name}'
        else:
            return None

    def calculate_rank(self):
        if self._elo > 0:
            self._rank = self._elo
        else:
            self._rank = CATEGORY[self._sex][self._category]
        return self
    
    def exist(self, name, surname):
        _exist = False
        if self.get_name() == name and self.get_surname() == surname:
            _exist = True
        else:
            _exist = False
        return _exist
    
    def set_round(self, round_nr, opponent_idnt, result=-1.0):
        while len(self._opponents) < round_nr:
            self._opponents.append(-1)
        while len(self._results) < round_nr:
            self._results.append(-1)
        self._opponents[round_nr-1] = opponent_idnt
        self._results[round_nr-1] = result

    def check_opponent_played(self, opponent_idnt):
        _played = False
        for opponent in self._opponents:
            if opponent == opponent_idnt and not _played:
                _played = True
        if opponent_idnt == self._idnt:
            _played = True
        return _played
    
    def refresh_possible_opponents(self, players):
        self._possible_opponents.clear()
        for player in players:
            if player._idnt != self._idnt and player._idnt not in self._opponents:
               self._possible_opponents.append(player._idnt)
        if not self._paused:
            self._possible_opponents.append(-1)


    def dump(self):
        _dump = f"\nPLAYER (#{self._idnt}): {self._name} {self._surname}\n"
        _dump += f"Sex: {self._sex}\n"
        # _dump += f"Birth: {self._birth_date}\n"
        _dump += f"City: {self._city}\n"
        _dump += f"Category: {self._category}\n"
        _dump += f"Elo rating: {self._elo}\n"
        _dump += f"Turnament rating: {self._rank}\n"
        return _dump
    
    def dump_short(self):
        _dump = f"\nPLAYER #{self._idnt}: {self._name} {self._surname}"
        return _dump

    def dump_opponents(self):
        _round_nr = 1
        _dump = "Opponents:\n"
        for oppo in self._opponents:
             _dump += f"Round {_round_nr}: #{oppo}, Result: {self._results[_round_nr-1]}\n"
             _round_nr += 1
        return _dump
    
    def dump_possible_opponents(self):
        _dump = f"Player: #{self._idnt} can play with:\n"
        for oppo in self._possible_opponents:
             _dump += f"{oppo}\n"
        return _dump


