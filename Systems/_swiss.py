"""_swiss.py

    System class with swiss system calculation model.

"""
# Global package imports:
import numpy as np
import logging

# Local package imports:
from Organization import Round
from Systems import System
from resources import SystemType


class SystemSwiss(System):

    """Swiss system for turnament run."""

    def __init__(self):
        self._round = 0
        self._type = SystemType.SWISS
        self.players: list

    def prepare_round(self, players: list, round_nr: int):
        self.players = players
        self._round = round_nr
        scored_players = self._sort_players()
        if self._round == 1:
            _round = self._set_tables_1(scored_players)
            msg_info = "Swiss system set. Players loaded."
            logging.info(msg=msg_info)
        else:
            _round = self._set_tables(scored_players)
        msg_info = f"Prepare round #{self._round}."
        logging.info(msg=msg_info)
        return _round

    def _sort_players(self):
        # Sort Players by turnamnt order
        scored_players = {}
        for point in np.arange(start=float(self._round), stop=-0.5, step=-0.5):
            scored_players[point] = []
            for player in self.players:
                if player.points == point:
                    scored_players[point].append(player)
        for point in np.arange(start=float(self._round), stop=-0.5, step=-0.5):
            scored_players[point].sort(key=lambda x: x.rank, reverse=True)
            scored_players[point].sort(key=lambda x: x.elo, reverse=True)
            scored_players[point].sort(key=lambda x: x.bucholz, reverse=True)
            scored_players[point].sort(key=lambda x: x.progress, reverse=True)
        return scored_players

    def _validate_sort(self, scored_players):
        pass

    def _itrate_sort(self, scored_players):
        pass

    def _round_one(self):
        pass

    def _round_next(self):
        pass

    def _set_tables_1(self, scored_players):
        """Set round 1."""
        _round = Round()
        _round.number = self._round
        scored_nums = {}

        # 1. Count number of Players per each score level
        for point in np.arange(start=float(self._round - 1), stop=-0.5, step=-0.5):
            scored_nums[point] = 0
            for player in scored_players[point]:
                if player.points == point:
                    scored_nums[point] += 1

        # 2. Foreach for point perspective groups:
        reserved_player = None
        for point in np.arange(start=float(self._round - 1), stop=-0.5, step=-0.5):

            # 2.1 Check if any Player from higher score group has to play with lower:
            if reserved_player:
                scored_nums[point] += 1
                scored_players[point].append(reserved_player)
                reserved_player = None

            # 2.2 Check if number of players are paired:
            not_paired = scored_nums[point] % 2 == 1
            if not_paired:
                reserved_player = scored_players[point][scored_nums[point] - 1]
                scored_nums[point] -= 1

            # 2.3 Set the tables with paired players:
            parity = 0
            scored_half_num = int(scored_nums[point] / 2)
            for i in range(0, scored_half_num):
                nr = _round.add_table(
                    player_w=scored_players[point][i].id,
                    player_b=scored_players[point][i + scored_half_num].id,
                )
                parity += 1
                if parity % 2 == 0:
                    _round.tables[nr].swap_players()

            # 2.4 Check id any player pausing:
            if reserved_player:
                _round.pausing = reserved_player.id
            # 2.5 Set flag 'paused' for particular player
            for player in self.players:
                if player.id == _round.pausing:
                    player.paused = True

        return _round

    def _set_tables(self, scored_players):
        parity = 0
        _round = Round()
        _round.number = self._round
        players_list = []  # plain list with sorted players
        players_set = []  # list of players IDs already paired

        # Set the tables with paired players
        # Begin with actual top Players, end with last ones:

        # 1. Put players into plain list:
        for point in np.arange(start=float(self._round - 1), stop=-0.5, step=-0.5):
            for player in scored_players[point]:
                players_list.append(player)

        # 2. Simple iterable for next player:
        for player in players_list:
            _no_pair_player = True

            # 2.1. Check if player alrady set in the round
            _played = False
            if player.id in players_set:
                _played = True

            # 2.2. If player is free pair Him/Her with an Opponnent:
            if not _played:
                opponent_found = False
                for opponent in players_list:

                    # 2.2.1 Check if opponent alrady set in the round
                    _oppo_played = False
                    if opponent.id in players_set:
                        _oppo_played = True
                    if opponent == player:
                        _oppo_played = True

                    # 2.2.2 Set next free Opponent to Player
                    if not opponent_found and not _oppo_played:
                        if (
                            # Check next free Opponent for player:
                            not opponent_found
                            # Check Opponent not yet played with Player:
                            and opponent.id not in player.opponents
                            # Simulate, that the rest of Players can be paired:
                            # @ToDo
                        ):
                            # OK, current Player and free Opponent match:
                            opponent_found = True  # Set flag, opponnent_found
                            _no_pair_player = False
                            players_set.append(player.id)  # Add players to 'set' list
                            players_set.append(opponent.id)
                            # Add table with these two players:
                            table_nr = _round.add_table(
                                player_w=player.id, player_b=opponent.id
                            )

                            parity += 1
                            # Swap order every odd table:
                            if parity % 2 == 0:
                                _round.tables[table_nr].swap_players()

                # 2.2.3. For Player without Opponent set 'pause':
                if _no_pair_player:
                    _round.pausing = player.id

        # 3. Check if pasuing is unique:
        _paused_right = True
        for player in players_list:
            _paused = 0
            for oppo in player.opponents:
                if oppo == -1:
                    _paused += 1
            if player.id == _round.pausing:
                _paused += 1
            if _paused > 1:
                _paused_right = False

        if not _paused_right:  # DEBUG
            msg_debug = f"Player {_round.pausing} has doubled pause!"
            logging.debug(msg=msg_debug)

        # 4. Find Player in the round, which can replace to pausing:
        _replace_ok = False
        _replace_pausing = _round.pausing
        _replace_opponent = -1
        # Get temporaty pausing Player:
        _paused_player = self._get_player(_round.pausing)
        if not _paused_right:
            for player in reversed(players_list):
                if (
                    player.id != _round.pausing and not _replace_ok
                ):  # Not the same player
                    # Get temporary Opponent:
                    _oppo_idnt = _round.get_opponent(player.id)
                    _oppo = self._get_player(_oppo_idnt)
                    # Check if temp pausing P did not play with Opponent
                    # and check if Opponent did not pause:
                    if _oppo_idnt not in _paused_player.opponents and not _oppo.paused:
                        _replace_opponent = _oppo_idnt
                        _replace_ok = True

        # 5. Replace Pausing Player with other Player:
        if not _paused_right and _replace_ok:  # DEBUG
            msg_debug = f"Replace pausing {_replace_pausing} with {_replace_opponent}!"
            logging.debug(msg=msg_debug)
            _round.change_player(
                player_old=_replace_opponent, player_new=_replace_pausing
            )
            _round.pausing = _replace_opponent
        # 5.1. Set flag 'paused' for particular player
        for player in self.players:
            if player.id == _round.pausing:
                player.paused = True

        # 6. Check for recalculating round again:
        if not _paused_right and _replace_ok:  # DEBUG
            msg_debug = (
                f"Round needs to be recalculated: {_round.pausing} cannot pause!"
            )
            logging.debug(msg=msg_debug)

        return _round
