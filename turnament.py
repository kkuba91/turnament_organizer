"""turnament.py

    Turnament class with edit, run and summary.
    Additional class with Player's data.

"""
# Global package imports:
from datetime import date
import logging

# Local package imports:
from Organization import set_system, Player, Round, SystemType


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
        self._system = SystemType.SWISS
        self._players = []
        self._rounds = []

        # Additional:
        self._place = ""

    def set_date(self, start, end):
        self._date_start = start
        self._date_end = end

    def add_player(
        self, name="", surname="", sex="male", city="", category="bk", elo=0
    ):
        _dont_add = False
        for p in self._players:
            if p.name == name and p.surname == surname:
                _dont_add = True
        if not _dont_add:
            player = Player()
            player.name = name
            player.surname = surname
            player.sex = sex
            player.city = city
            player.category = category
            player.elo = elo
            player.calculate_rank()
            self._players.append(player)
            self._players_num += 1

    def del_player(self, name="", surname=""):
        for player in self._players:
            if player.exist(name=name, surname=surname):
                self._players.pop(player)

    def add_result(self, table_nr, result):
        self._rounds[self._act_round_nr - 1].tables[table_nr].result = result

    def begin(self, rounds):
        if isinstance(rounds, int):
            if 0 < rounds < 23 and self._players_num > 1:
                self._begin(rounds)

    def _begin(self, rounds):
        self._rounds_num = rounds
        self._act_round_nr = 1
        self._players.sort(key=lambda x: x.rank, reverse=True)
        self._players.sort(key=lambda x: x.elo, reverse=True)
        ident = 1
        for player in self._players:
            player.id = ident
            ident += 1
        system = set_system(self._system)
        self._rounds.append(system.prepare_round(self._players, self._act_round_nr))
        self._players = system.players

    def next_round(self):
        if self._act_round_nr < self._rounds_num:
            self._act_round_nr += 1
            system = set_system(self._system)
            self._rounds.append(system.prepare_round(self._players, self._act_round_nr))
            self._players = system.players
            _ret = None
        else:
            _ret = -1
            msg_log = f"[Error] Maximum turnament round: {self._rounds_num}!!"
            logging.info(msg=msg_log)
        return _ret

    def apply_round_results(self):
        # Handle if wrong type passed
        # @todo: check out if all results are commited
        self._rounds[self._act_round_nr - 1].all_results = True
        _round = self._rounds[self._act_round_nr - 1]
        if not isinstance(_round, Round):
            return None
        elif not _round.all_results:
            msg_info = (
                "Cannot perform apply round results, "
                "because not all results are commited."
            )
            logging.info(msg=msg_info)
            return None
        # Move results of tables to player scores:
        for t_key in _round.tables:
            table = _round.tables[t_key]

            msg_debug = "Check table.dump():"
            logging.debug(msg=msg_debug)
            logging.debug(msg=table.dump())

            for player in self._players:
                if player.id == table.w_player:
                    player.points += table.result
                    player.progress += player.points
                    player.add_opponent(table.b_player)
                    player.refresh_possible_opponents(self._players)
                    player.add_result(table.result)
                    player.round_done()
                if player.id == table.b_player:
                    player.points += 1.0 - table.result
                    player.progress += player.points
                    player.add_opponent(table.w_player)
                    player.refresh_possible_opponents(self._players)
                    player.add_result(1.0 - table.result)
                    player.round_done()
        if _round.pausing > 0:
            for player in self._players:
                if player.id == _round.pausing:
                    player.points += 1
                    player.progress += player.points
                    player.add_opponent(-1)
                    player.add_result(1.0)
                    msg_debug = f"Pausing: #{ _round.pausing}"
                    logging.debug(msg=msg_debug)
        # Calculate bucholz for each player after the round:
        for player in self._players:
            _bucholz = 0.0
            for opponent_idnt in player.opponents:
                for opponent in self._players:
                    if opponent.id == opponent_idnt:
                        _bucholz += opponent.points
            player.bucholz = _bucholz
        # Sort players:
        self._players.sort(key=lambda x: x.bucholz, reverse=True)
        self._players.sort(key=lambda x: x.progress, reverse=True)
        self._players.sort(key=lambda x: x.points, reverse=True)

    def delete_players(self):
        if self._players:
            self._players.clear()

    def dump_act_results(self):
        _dump = f"RESULTS AFTER ROUND NR: #{self._act_round_nr}:\n\n"
        _dump1 = "#Id:  PLAYER: "
        _dump2 = "\tPTS:  \tPROG:  \tBUCH: \tRANK: \tCAT:\n"
        _dump += "{0:<34}".format(_dump1) + _dump2
        for player in self._players:
            _dump1 = f"#{player.id}    {player.surname} {player.name}: "
            _dump2 = (
                f"\t{player.points}  \t{player.progress}  \t{player.bucholz} "
                f"\t{player.rank} \t{player.category}\n"
            )
            _dump += "{0:<34}".format(_dump1) + _dump2
        return _dump

    def dump_players(self):
        _dump = "PLAYERS - LIST:"
        for player in self._players:
            _dump += player.dump()
            _dump += player.dump_opponents()
        return _dump

    def dump_players_p_o(self):
        _dump = "PLAYERS - POSSIBLE OPPONENTS:\n"
        for player in self._players:
            _dump += player.dump_possible_opponents()
        return _dump

    def dump(self):
        _dump = f"TURNAMENT: {self._name}\n"
        _dump += f" Place: {self._place}\n"
        # _dump += f'Time: {self._date_start} to {self._date_end}\n\n'
        _dump += f" Players: {self._players_num}\n"
        _dump += f" Round actual: {self._act_round_nr}\n"
        _dump += f" Rounds: {self._rounds_num}\n"
        _dump += self._rounds[self._act_round_nr - 1].dump()
        return _dump
