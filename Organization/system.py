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
    
    def _get_player(self, _idnt):
        _ret_p = None
        for player in self._players:
            if player._idnt == _idnt:
                _ret_p = player
        return _ret_p


class SystemSchweiz(System):
    def __init__(self):
        self._round = 0
        self._type = 'Schweiz'
        self._players: list
    
    def prepare_round(self, players: list, _round: int):
        self._players = players
        self._round = _round
        # print('Schweiz system set. Players loaded.')
        scored_players = self._sort_players()
        if self._round == 1:
            _round = self._set_tables_1(scored_players)
        else:
            _round = self._set_tables(scored_players)
        # print(_round.dump())
        return _round
    
    def _sort_players(self):
        # Sort Players by turnamnt order
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

    def _round_one(self):
        pass

    def _round_next(self):
        pass

    def _set_tables_1(self, scored_players):
        pairity = 0
        player_w = 0
        player_b = 0
        _round = Round()
        _round.number = self._round
        scored_nums = dict()
        
        # 1. Count number of Players per each score level
        for point in np.arange(start=float(self._round-1), stop=-0.5, step=-0.5):
            scored_nums[point] = 0
            for player in scored_players[point]:
                if player._points == point:
                    scored_nums[point] += 1
                    player._set = False

        # 2. Foreach for point perspective groups:
        reserved_player = None
        for point in np.arange(start=float(self._round-1), stop=-0.5, step=-0.5):

            # 2.1 Check if any Player from higher score group has to play with lower:
            if reserved_player:
                scored_nums[point] += 1
                scored_players[point].append(reserved_player)
                reserved_player = None

            # 2.2 Check if number of players are paired:
            not_paired = (scored_nums[point] % 2 == 1)
            if not_paired:
                reserved_player = scored_players[point][scored_nums[point]-1]
                scored_nums[point] -= 1
            
            # 2.3 Set the tables with paired players:
            parity = 0
            scored_half_num = int(scored_nums[point]/2)
            for i in range(0, scored_half_num):
                nr = _round.add_table(
                            player_w=scored_players[point][i]._idnt,
                            player_b=scored_players[point][i+scored_half_num]._idnt
                        )
                parity += 1
                if parity % 2 == 0:
                    _round.tables[nr].swap_players()
            
            # 2.4 Check id any player pausing:
            if reserved_player:
                _round.pausing = reserved_player._idnt
            # 2.5 Set flag 'paused' for particular player
            for player in self._players:
                if player._idnt == _round.pausing:
                    player._paused = True
            
        return _round

    def _set_tables(self, scored_players):
        parity = 0
        _round = Round()
        _round.number = self._round
        players_list = list()  # plain list with sorted players
        players_set = list()  # list of players IDs already paired

        # Set the tables with paired players
        # Begin with actual top Players, end with last ones:

        # 1. Put players into plain list:
        for point in np.arange(start=float(self._round-1), stop=-0.5, step=-0.5):
            for player in scored_players[point]:
                players_list.append(player)

        # 2. Simple iterable for next player:
        for player in players_list:
            _no_pair_player = True
            
            # 2.1. Check if player alrady set in the round
            _played = False
            for p in players_set:
                if p == player._idnt:
                    _played = True

            # 2.2. If player is free pair Him/Her with an Opponnent:
            if not _played:
                opponent_found = False
                for opponent in players_list:

                    # 2.2.1 Check if opponent alrady set in the round
                    _oppo_played = False
                    for p in players_set:
                        if p == opponent._idnt:
                            _oppo_played = True
                    if opponent._idnt == player._idnt:
                        _oppo_played = True

                    # 2.2.2 Set next free Opponent to Player
                    if not opponent_found and not _oppo_played:
                        # Check next free Opponent for player and not played with Player:
                        if not opponent_found and opponent._idnt not in player._opponents:
                            # OK, current Player and free Opponent match:
                            opponent_found = True  # Set flag, opponnent_found
                            _no_pair_player = False
                            players_set.append(player._idnt)  # Add players to 'set' list
                            players_set.append(opponent._idnt)
                            # Add table with these two players:
                            nr = _round.add_table(
                                        player_w=player._idnt,
                                        player_b=opponent._idnt
                                    )

                            parity += 1
                            # Swap order every odd table:
                            if parity % 2 == 0:
                                _round.tables[nr].swap_players()

                # 2.2.3. For Player without Opponent set 'pause':
                if _no_pair_player:
                    _round.pausing = player._idnt

        # 3. Check if pasuing is unique:
        _paused_right = True
        for player in players_list:
            _paused = 0
            for oppo in player._opponents:
                if oppo == -1:
                    _paused += 1
            if player._idnt == _round.pausing:
                _paused += 1
            if _paused > 1:
                _paused_right = False
            
        if not _paused_right:  # DEBUG
            print(f'[DEBUG] Player {_round.pausing} has doubled pause!')
        
        # 4. Find Player in the round, which can replace to pausing:
        _replace_ok = False
        _replace_pausing = _round.pausing
        _replace_opponent = -1
        # Get temporaty pausing Player:
        _paused_player = self._get_player(_round.pausing)
        if not _paused_right:
            for player in reversed(players_list):
                if player._idnt != _round.pausing and not _replace_ok:  # Not the same player
                    # Get temporary Opponent:
                    _oppo_idnt = _round.get_opponent(player._idnt)
                    _oppo = self._get_player(_oppo_idnt)
                    # Check if temp pausing P did not play with Opponent and check if Opponent did not pause:
                    if _oppo_idnt not in _paused_player._opponents and not _oppo._paused:
                        _replace_opponent = _oppo_idnt
                        _replace_ok = True

        
        # 5. Replace Pausing Player with other Player:
        if not _paused_right and _replace_ok:  # DEBUG
            print(f'[DEBUG] Replace pausing {_replace_pausing} with {_replace_opponent}!')
            _round.change_player(player_old=_replace_opponent, player_new=_replace_pausing)
            _round.pausing = _replace_opponent
        # 5.1. Set flag 'paused' for particular player
        for player in self._players:
            if player._idnt == _round.pausing:
                player._paused = True

        # 6. Check for recalculating round again:
        if not _paused_right and _replace_ok:  # DEBUG
            print(f'[DEBUG] Round needs to be recalculated: {_round.pausing} cannot pause!')
        

        return _round


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
