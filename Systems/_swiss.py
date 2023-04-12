"""_swiss.py

    System class with swiss system calculation model.

"""
# Global package imports:
import numpy as np
import logging

# Local package imports:
from Organization import Round
from Organization.player import Player
from Systems import System
from Resources import SystemType


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

        # 2. Foreach point perspective groups:
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
    
    def _validate_with_next_pairing_2(self, players_list: list, players_set: list, act_player, act_opponent):
        """Deph 2 validation."""
        p_list = players_list.copy()
        p_set = players_set.copy()
        p_set.append(act_player.id)
        p_set.append(act_opponent.id)

        p_available = [player for player in p_list if (player.id not in p_set)]
        p_available_qty = len(p_available)
        covered = 0

        for i in range(len(players_list)):
            # 2. Simple iterable for next Player to play:
            p_available = [player for player in p_list if (player.id not in p_set)]
            for player in p_available:
                # 2.1. List of available Opponents:
                opponent_found = False
                player.refresh_possible_opponents(players_list)
                for opponent in player.possible_opponents:
                    # 2.1.2 Set next free Opponent to Player
                    if not opponent_found and opponent.id not in player.opponents:
                        if player.id not in p_set and opponent.id not in p_set:
                            # OK, current Player and free Opponent match:
                            opponent_found = True  # Set flag, opponnent_found
                            p_set.append(player.id)
                            p_set.append(opponent.id)
                            covered += 2
                            player.refresh_possible_opponents(players_list)
        return covered >= p_available_qty

    def _validate_with_next_pairing(self, players_list: list, players_set: list, act_player, act_opponent):
        """Deph 1 validation."""
        p_list = players_list.copy()
        p_set = players_set.copy()
        p_set.append(act_player.id)
        p_set.append(act_opponent.id)

        p_available = [player for player in p_list if (player.id not in p_set)]
        p_available_qty = len(p_available)
        covered = 0

        for i in range(len(players_list)):
            # 2. Simple iterable for next Player to play:
            p_available = [player for player in p_list if (player.id not in p_set)]
            for player in p_available:
                # 2.1. List of available Opponents:
                opponent_found = False
                player.refresh_possible_opponents(players_list)
                for opponent in player.possible_opponents:
                    # 2.1.2 Set next free Opponent to Player
                    if not opponent_found and opponent.id not in player.opponents:
                        if player.id not in p_set and opponent.id not in p_set:
                            # OK, current Player and free Opponent match:
                            if self._validate_with_next_pairing_2(p_list, p_set, player, opponent):
                                opponent_found = True  # Set flag, opponnent_found
                                p_set.append(player.id)
                                p_set.append(opponent.id)
                                covered += 2
                                player.refresh_possible_opponents(players_list)
        return covered >= p_available_qty

    def _set_tables(self, scored_players):
        """Set round N, where N > 1)."""
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
        # 1.1 Add optional Pauser (fantom opponent for pausing Player) to the end:
        if len(players_list) % 2 == 1:
            players_list.append(Player(pauser=True))
        
        # 1.2 Dump possible opponents:
        for player in players_list:
            player.refresh_possible_opponents(players_list)

        # 2. Simple iterable for next Player to play:
        p_available = [player for player in players_list if (player.id not in players_set)]
        for player in p_available:
            # 2.1. List of available Opponents:
            opponent_found = False
            player.refresh_possible_opponents(players_list)
            for opponent in player.possible_opponents:
                # 2.1.2 Set next free Opponent to Player
                if not opponent_found and opponent.id not in player.opponents:
                    if player.id not in players_set and opponent.id not in players_set:
                        # OK, current Player and free Opponent match:
                        if self._validate_with_next_pairing(players_list, players_set, player, opponent):
                            opponent_found = True  # Set flag, opponnent_found
                            players_set.append(player.id)  # Add players to 'set' list
                            players_set.append(opponent.id)
                            # Add table with these two players:
                            table_nr = _round.add_table(
                                player_w=player.id, player_b=opponent.id
                            )
                            player.refresh_possible_opponents(players_list)

                            # 2.1.3 Check if Opponent is not a Pauser:
                            parity += 1
                            if opponent.id == -1:
                                _round.pausing = player.id
                                player.paused = True

                            # Swap order every odd table:
                            elif parity % 2 == 0:
                                _round.tables[table_nr].swap_players()

            p_available = [player for player in players_list if (player.id not in players_set)]
        return _round
