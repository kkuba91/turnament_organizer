"""_circular.py

    System class with circular system calculation model.

"""
# Global package imports:
import numpy as np
import logging

# Local package imports:
from Organization import Round
from Systems import System
from resources import SystemType


class SystemCircular(System):
    def __init__(self):
        self._round = 0
        self._type = SystemType.CIRCULAR
        self.players: list

    def prepare_round(self, players: list, round_nr: int):
        self.players = players
        self._round = round_nr
        self._sort_players()

    def _sort_players(self):
        pass
