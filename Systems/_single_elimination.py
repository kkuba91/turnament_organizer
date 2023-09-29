"""_single_elimination.py

    System class with single elimination system calculation model.

"""
# Global package imports:

# Local package imports:
from Systems import System
from resources import SystemType


class SystemSingleElimination(System):
    def __init__(self):
        self._round = 0
        self._type = SystemType.SINGLE_ELIMINATION
        self.players = []

    def prepare_round(self, players: list, round_nr: int):
        self.players = players
        self._round = round_nr

    def _sort_players(self):
        return self._sort_players()
