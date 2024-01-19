"""_base.py

    Base System class with methods declaration.

"""
# Global package imports:
from abc import ABC, abstractmethod
import logging

# Local package imports:

MSG_COMMON = "Uninitiated system type. Not allowed to invoke method "


class System(ABC):
    @abstractmethod
    def __init__(self, sys_type: int):
        self._round = 0
        self.players: list
        self.type = sys_type

    @abstractmethod
    def prepare_round(self, *args, **kwargs):
        msg_debug = MSG_COMMON + "'prepare_round'"
        logging.debug(msg=msg_debug)

    def _get_player(self, _idnt):
        # Getter from a list of playing Players.
        _ret_p = None
        for player in self.players:
            if player.id == _idnt:
                _ret_p = player
        return _ret_p

    def _sort_players(self, *args, **kwargs):
        # Sort Players by turnamnt order
        msg_debug = MSG_COMMON + "'_sort_players'"
        logging.debug(msg=msg_debug)

    def _validate_sort(self, *args, **kwargs):
        msg_debug = MSG_COMMON + "'_validate_sort'"
        logging.debug(msg=msg_debug)

    def _itrate_sort(self, *args, **kwargs):
        msg_debug = MSG_COMMON + "'_itrate_sort'"
        logging.debug(msg=msg_debug)

    def _round_one(self, *args, **kwargs):
        msg_debug = MSG_COMMON + "'_round_one'"
        logging.debug(msg=msg_debug)

    def _round_next(self, *args, **kwargs):
        msg_debug = MSG_COMMON + "'_round_next'"
        logging.debug(msg=msg_debug)

    def _set_tables_1(self, *args, **kwargs):
        """[Optional] Some systems have odd the first round pairing."""
        msg_debug = MSG_COMMON + "'_set_tables_1'"
        logging.debug(msg=msg_debug)

    def _set_tables(self, *args, **kwargs):
        """Normal round pairing."""
        msg_debug = MSG_COMMON + "'_set_tables'"
        logging.debug(msg=msg_debug)
