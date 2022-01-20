"""turnament.py

    Turnament class with edit, run and summary.
    Additional class with Player's data.

"""
# Global package imports:
from datetime import date

# Local package imports:
from Organization.system import System, set_system
from Organization.player import Player
from Organization.round import Round


class Turnament(object):
    def __init__(self, name) -> None:
        # General:
        self._name = name
        self._date_start: date
        self._date_end: date
        self._players_num = 0
        self._mean_rank = 0
        self._mean_age = 0
        self._rounds_num = 0
        self._act_round_nr = 0
        self._system = 'Schweiz'
        self._players = list()
        self._rounds = list()

        # Additional:
        self._place = ""
    
    def set_date(self, start, end):
        self._date_start = start
        self._date_end = end

    def add_player(self, name = "", surname = "", sex = "male",
        city = "", category = "bk", elo = 0):
        _dont_add = False
        for p in self._players:
            if p._name == name and p._surname == surname:
                _dont_add = True
        if not _dont_add:
            player = Player()
            player.set_name(name).set_surname(surname).set_sex(sex)
            player.set_city(city)
            player.set_category(category).set_elo(elo)
            player.calculate_rank()
            self._players.append(player)
            self._players_num += 1
    
    def del_player(self, name = "", surname = ""):
        for player in self._players:
            if player.exist(name=name, surname=surname):
                self._players.pop(player)
    
    def add_result(self, table_nr, result):
        self._rounds[self._act_round_nr-1].tables[table_nr].result = result

    def begin(self, rounds):
        if isinstance(rounds, int):
            if 0 < rounds < 23 and self._players_num > 1:
                self._begin(rounds)

    def _begin(self, rounds):
        self._rounds_num = rounds
        self._act_round_nr = 1
        self._players.sort(key=lambda x: x._rank, reverse=True)
        self._players.sort(key=lambda x: x._elo, reverse=True)
        ident = 1
        for player in self._players:
            player._idnt = ident
            ident += 1
        system = set_system(self._system)
        self._rounds.append(system.prepare_round(self._players, self._act_round_nr))
    
    def next_round(self):
        if self._act_round_nr < self._rounds_num:
            self._act_round_nr += 1
            system = set_system(self._system)
            self._rounds.append(system.prepare_round(self._players, self._act_round_nr))

    def apply_round_results(self):
        # Handle if wrong type passed
        # @todo: check out if all results are commited
        self._rounds[self._act_round_nr-1].all_results = True
        _round = self._rounds[self._act_round_nr-1]
        if not isinstance(_round, Round):
            return None
        elif not _round.all_results:
            _log = 'Cannot perform apply round results, ' + \
                   'because not all results are commited.'
            print(_log)
            return None
        # Move results of tables to player scores:
        for t_key in _round.tables:
            table = _round.tables[t_key]
            print('Check table.dump():')
            print(table.dump())
            print('\n')
            for player in self._players:
                if player._idnt == table.w_player:
                    player._points += table.result
                    player._progress += player._points
                    player._oponents.append(table.b_player)
                    player._results.append(table.result)
                    player._round_done = True
                if player._idnt == table.b_player:
                    player._points += (1.0 - table.result)
                    player._progress += player._points
                    player._oponents.append(table.w_player)
                    player._results.append(1.0 - table.result)
                    player._round_done = True
        if _round.pausing > 0:
            for player in self._players:
                if player._idnt == _round.pausing:
                    player._points += 1
                    player._progress += player._points
        # Calculate bucholz for each player aftr the round:
        for player in self._players:
            _bucholz = 0.0
            for opponent_idnt in player._oponents:
                for opponent in self._players:
                    if opponent._idnt == opponent_idnt:
                        _bucholz += opponent._points
            player._bucholz = _bucholz
        # Sort players:
        self._players.sort(key=lambda x: x._bucholz, reverse=True)
        self._players.sort(key=lambda x: x._progress, reverse=True)
        self._players.sort(key=lambda x: x._points, reverse=True)
    
    def dump_act_results(self):
        _dump = f'RESULTS AFTER ROUND NR: #{self._act_round_nr}:\n\n'
        _dump1 = f'#Id:  PLAYER: '
        _dump2 = f'\tPTS:  \tPROG:  \tBUCH: \tRANK: \tCAT:\n'
        _dump += "{0:<34}".format(_dump1) + _dump2
        for player in self._players:
            _dump1 = f'#{player._idnt}    {player._surname} {player._name}: '
            _dump2 = f'\t{player._points}  \t{player._progress}  \t{player._bucholz} \t{player._rank} \t{player._category}\n'
            _dump += "{0:<34}".format(_dump1) + _dump2
        return _dump
    
    def dump_players(self):
        _dump = f'PLAYERS - LIST:'
        for player in self._players:
            _dump += player.dump()
        return _dump

    def dump(self):
        _dump = f'TURNAMENT: {self._name}\n'
        _dump += f' Place: {self._place}\n'
        # _dump += f'Time: {self._date_start} to {self._date_end}\n\n'
        _dump += f' Players: {self._players_num}\n'
        _dump += f' Round actual: {self._act_round_nr}\n'
        _dump += f' Rounds: {self._rounds_num}\n'
        _dump += self._rounds[self._act_round_nr - 1].dump()
        return _dump
    


        