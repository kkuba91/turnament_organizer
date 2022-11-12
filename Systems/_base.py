"""_base.py

    System class with calculation model, players organization and ranks estimation.
    This class is strictly related with class Player, Round - must be.

"""
# Global package imports:
from abc import ABC, abstractmethod
import numpy as np
import logging

# Local package imports:


class System(ABC):
    @abstractmethod
    def __init__(self, sys_type: int):
        self._round = 0
        self.players: list
        self.type = sys_type

    @abstractmethod
    def prepare_round(self, *args, **kwargs):
        pass

    def _sort_players(self, *args, **kwargs):
        pass

    def _get_player(self, _idnt):
        # Getter from a list of playing Players.
        _ret_p = None
        for player in self.players:
            if player.id == _idnt:
                _ret_p = player
        return _ret_p

    def _sort_players(self, *args, **kwargs):
        # Sort Players by turnamnt order
        pass

    def _validate_sort(self, *args, **kwargs):
        pass

    def _itrate_sort(self, *args, **kwargs):
        pass

    def _round_one(self, *args, **kwargs):
        pass

    def _round_next(self, *args, **kwargs):
        pass

    def _set_tables_1(self, *args, **kwargs):
        """[Optional] Some of systems have odd the first round pairing."""
        pass

    def _set_tables(self, *args, **kwargs):
        """Normal round pairing."""
        pass
