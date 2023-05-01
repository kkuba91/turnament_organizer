"""turnament.py

    Turnament class with edit, run and summary.
    Additional class with Player's data.

"""
# Global package imports:
from datetime import date
import logging
from pydantic import ValidationError
from tabulate import tabulate

# Local package imports:
from Organization import Player, Round
from Systems import get_system
from Resources import SystemType, SystemNames


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
        self.fine_to_begin = False
        self._system = SystemType.UNKNOWN
        self._players = []
        self._rounds = []

        # Additional:
        self._place = ""
    
    @property
    def players_num(self):
        self._players_num = len(self._players)
        return self._players_num
    
    def set_system(self, system_id: int):
        if self._act_round_nr == 0:
            msg_info = f"Set {SystemNames[system_id]} round pairing system."
            logging.info(msg=msg_info)
            self._system = system_id

    def set_date(self, start, end):
        self._date_start = start
        self._date_end = end

    def add_player(
        self, name="", surname="", sex="male", city="", category="bk", elo=0
    ):
        # Validate Player add:
        _dont_add = False
        for p in self._players:
            if p.name == name and p.surname == surname:
                _dont_add = True
                msg_error_1 = "\nPlayer {} {} already set into turnament.".format(name, surname)
                logging.error(msg=msg_error_1)
        # Add Player:
        if not _dont_add:
            try:
                player = Player(
                    name=name,
                    surname=surname,
                    sex=sex,
                    city=city,
                    category=category,
                    elo=elo
                )
            except ValidationError as exc:
                msg_error_2 = "\nCannot add Player with invalid data."
                logging.error(msg=str(exc) + msg_error_2)
            else:
                self._players.append(player)
                msg_info = f"Set Player: {player.name} {player.surname}, " + \
                        f"[elo: {player.elo}, cat: {player.category}] in turnament."
                logging.info(msg=msg_info)

    def del_player(self, name="", surname=""):
        for player in self._players:
            if player.exist(name=name, surname=surname):
                msg_info = f"Remove: {player.name} " + \
                           f"{player.surname} from turnament."
                logging.info(msg=msg_info)
                self._players.pop(player)
            else:
                msg_info = f"No Player #{player.id} on turnament list."
                logging.info(msg=msg_info)

    def add_result(self, table_nr, result):
        round_id = self._act_round_nr - 1
        if self.fine_to_begin:
            try:
                self._rounds[round_id].set_result(table_nr, result)
            except KeyError as exc:
                msg_error = f"Used values: round_id={round_id}, table_nr={table_nr}. ({exc})"
                logging.error(msg=msg_error)
        else:
            msg_error = f"Something is wrong, turnament did not start. System {SystemNames[self._system]}."
            logging.error(msg=msg_error)

    def begin(self, rounds):
        if isinstance(rounds, int):
            if self._system == SystemType.UNKNOWN:
                msg_error = "Please set pairing system for turnament."
                logging.error(msg=msg_error)
            elif 0 < rounds < 23 and self.players_num > 1:
                self.fine_to_begin = True
                self._begin(rounds)
            else:
                msg_error = "Please add more Players to the event."
                logging.error(msg=msg_error)

    def _begin(self, rounds):
        self._rounds_num = rounds
        self._act_round_nr = 1
        self._players.sort(key=lambda x: x.rank, reverse=True)
        self._players.sort(key=lambda x: x.elo, reverse=True)
        ident = 1
        for player in self._players:
            if not player.pauser:
                player.id = ident
                ident += 1
        system = get_system(self._system)
        self._rounds.append(system.prepare_round(self._players, self._act_round_nr))
        self._players = system.players

    def next_round(self):
        _ret = None
        if self._act_round_nr < self._rounds_num:
            self._act_round_nr += 1
            system = get_system(self._system)
            self._rounds.append(system.prepare_round(self._players, self._act_round_nr))
            self._players = system.players
            _ret = None
        else:
            _ret = -1
            msg_error = f"Maximum turnament round: {self._rounds_num}!!"
            logging.error(msg=msg_error)
        return _ret

    def apply_round_results(self):
        # Handle if wrong type passed
        if not self.fine_to_begin:
            msg_error = "Round cannot be started. Check turnament settings."
            logging.error(msg=msg_error)
            return None
        elif not self._rounds[self._act_round_nr - 1].all_results:
            msg_error = f"Not all results have been applied yet! {self._rounds[self._act_round_nr - 1].dump()}"
            logging.error(msg=msg_error)
            return None
        _round = self._rounds[self._act_round_nr - 1]
        if not isinstance(_round, Round):
            return None
        # Move results of tables to player scores:
        for t_key in _round.tables:
            table = _round.tables[t_key]

            msg_debug = "Check table.dump():"
            logging.debug(msg=msg_debug)
            logging.debug(msg=table.dump())

            for player in self._players:
                if player.id == table.w_player and player.id != _round.pausing:
                    player.points += table.result
                    player.progress += player.points
                    player.add_opponent(table.b_player)
                    player.add_result(table.result)
                    player.round_done = True
                if player.id == table.b_player and player.id != _round.pausing:
                    player.points += 1.0 - table.result
                    player.progress += player.points
                    player.add_opponent(table.w_player)
                    player.add_result(1.0 - table.result)
                    player.round_done = True
        if _round.pausing > 0:
            for player in self._players:
                if player.id == _round.pausing and player.id > 0:
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

    def get_players(self, type='results'):
        data = {
            'quntity': len(self._players),
            'players': []
        }
        specific = []
        if type == 'results':
            specific = ['id', 'name', 'surname', 'cat', 'elo', 'result', 'progress', 'bucholz']
        elif type == 'start':
            specific = ['id', 'name', 'surname', 'cat', 'elo', 'club', 'city', 'sex']
        for player in self._players:
            data["players"].append(player.get(specific=specific))
        if type == 'start':
            data["players"].sort(key=lambda x: x['id'], reverse=True)
        else:
            data["players"].sort(key=lambda x: x['bucholz'], reverse=True)
            data["players"].sort(key=lambda x: x['progress'], reverse=True)
            data["players"].sort(key=lambda x: x['result'], reverse=True)
        return data


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
        _dump += f" Players: {self.players_num}\n"
        _dump += f" Round actual: {self._act_round_nr}\n"
        _dump += f" Rounds: {self._rounds_num}\n"
        if self._act_round_nr > 0:
            _dump += self._rounds[self._act_round_nr - 1].dump()
        return _dump
    
    def __repr__(self) -> str:
        return self.dump().replace('\n', ',')
