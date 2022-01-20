"""system.py

    System class with calculation model, players organization and ranks estimation.
    This class is strictly related with class Player, Round - must be.

"""
# Global package imports:
from abc import ABC, abstractmethod
import numpy as np

# Local package imports:
from Organization.player import Player
from Organization.round import Round
from Organization.table import Table


def set_system(ttype):
    if ttype == 'Schweiz':
        return SystemSchweiz()
    if ttype == 'Circular':
        return SystemCircular()
    if ttype == 'SingleElimination':
        return SystemSingleElimination()


class System(ABC):
    @abstractmethod
    def __init__(self, ttype):
        self._round = 0
        self._players: list
        if ttype == 'Schweiz':
            self = SystemSchweiz
        if ttype == 'Circular':
            self = SystemCircular
        if ttype == 'SingleElimination':
            self = SystemSingleElimination

    @abstractmethod
    def prepare_round(self, players: list, round):
        pass

    def _sort_players(self):
        pass


class SystemSchweiz(System):
    def __init__(self):
        self._round = 0
        self._type = 'Schweiz'
        self._players: list
    
    def prepare_round(self, players: list, _round: int):
        self._players = players
        self._round = _round
        print('Schweiz system set. Players loaded.')
        scored_players = self._sort_players()
        _round = self._set_tables(scored_players)
        return _round
    
    def _sort_players(self):
        scored_players = dict()
        for point in np.arange(start=float(self._round), stop=-0.5, step=-0.5):
            scored_players[point] = []
            for player in self._players:
                if player._points == point:
                    scored_players[point].append(player)
        for point in np.arange(start=float(self._round), stop=-0.5, step=-0.5):
            scored_players[point].sort(key=lambda x: x._rank, reverse=True)
            scored_players[point].sort(key=lambda x: x._elo, reverse=True)
            scored_players[point].sort(key=lambda x: x._bucholz, reverse=True)
            scored_players[point].sort(key=lambda x: x._progress, reverse=True)
        return scored_players
    
    def _validate_sort(self, scored_players):
        pass

    def _itrate_sort(self, scored_players):
        pass

    def _set_tables(self, scored_players):
        pairity = 0
        player_w = 0
        player_b = 0
        round = Round()
        round.number = self._round
        scored_nums = dict()
        
        # Count number of Players per each score level
        for point in np.arange(start=float(self._round-1), stop=-0.5, step=-0.5):
            scored_nums[point] = 0
            for player in scored_players[point]:
                if player._points == point:
                    scored_nums[point] += 1
                    player._set = False
            print(f'Scored {point} have: {scored_nums[point]} players')

        nums = 0
        reserved_player = None
        for point in np.arange(start=float(self._round-1), stop=-0.5, step=-0.5):
            nums = 0

            # Check if any Player from higher score group has to play with lower:
            if reserved_player:
                scored_nums[point] += 1
                scored_players[point].append(reserved_player)
                reserved_player = None

            # Check if numbr of players are paired:
            not_paired = (scored_nums[point] % 2 == 1)
            if not_paired:
                reserved_player = scored_players[point][scored_nums[point]-1]
                scored_nums[point] -= 1
            
            # Set the tables with paired players:
            parity = 0
            scored_half_num = int(scored_nums[point]/2)
            for i in range(0, scored_half_num):
                nr = round.add_table(
                    player_w=scored_players[point][i]._idnt,
                    player_b=scored_players[point][i+scored_half_num]._idnt
                    )
                parity += 1
                if parity % 2 == 0:
                    round.tables[nr].swap_players()
            
            # Check id any player pausing:
            if reserved_player:
                round.pausing = reserved_player._idnt
        return round





class SystemCircular(System):
    def __init__(self):
        self._round = 0
        self._type = 'Circular'
        self._players: list
    
    def prepare_round(self, players: list, round: int):
        self._players = players
        self._round = round
        self._sort_players()
    
    def _sort_players(self):
        pass


class SystemSingleElimination(System):
    def __init__(self):
        self._round = 0
        self._type = 'SingleElimination'
        self._players: list
    
    def prepare_round(self, players: list, round: int):
        self._players = players
        self._round = round
    
    def _sort_players(self):
        return super()._sort_players()
