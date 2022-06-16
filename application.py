"""application.py

    Application class with initailization, run and ending.

"""
# Global package imports:
import os
from abc import ABC

# Local package imports:
from browser import Browser
from command import Command
from turnament import Turnament


DEBUG = True
class Application:
    def __init__(self, name):
        self._name = name
        self._end = False
        self._is_db_opened = False
        self._is_browser_opened = False
        self._browser: None
        self._cmd: None
        self._turnament: None
        print(f'Starting "{name}" application.. ')
    
    def init(self):
        self._browser = Browser()
        self._cmd = Command()

    def run(self):
        while not self._end:
            self.choice(method='cmd')
            self.dir_help()
            self.dir_new()
            self.dir_open()
            self.dir_close()
            self.dir_end()
            self.dir_debug()

    def end(self):
        pass

    def choice(self, method='cmd', cmd=''):
        if method == 'cmd':
            self._cmd.input_std()
        else:
            self._cmd.input_set(cmd)

    def dir_help(self):
        if self._cmd.check_cmd('help'):
                print('SELECT ONE OF: New, Open, Close, End')
    
    def dir_new(self):
        if self._cmd.check_cmd('New'):
                if self._cmd.is_params():
                    self._browser.set_file(path='C:', filename=self._cmd.get_param(0))
                    self._browser.get_file(option=self._cmd.get_cmd())
                    self._turnament = Turnament(name=self._cmd.get_param(0))
    
    def dir_open(self):
        if self._cmd.check_cmd('Open'):
                if self._cmd.is_params():
                    self._browser.set_file(path='C:', filename=self._cmd.get_param(0))
                    self._browser.get_file(option=self._cmd.get_cmd())
                    self._turnament = Turnament(name=self._cmd.get_param(0))
    
    def dir_close(self):
        if self._cmd.check_cmd('Close'):
                self._browser.stop()
                self._turnament._players.clear()
    
    def dir_end(self):
        if self._cmd.check_cmd('End'):
                self._end = True

    def dir_debug(self):
        if self._cmd.check_cmd('debug') and DEBUG:
            os.system('cls' if os.name == 'nt' else 'clear')
            if self._turnament:
                self._turnament.add_player(
                    name = "Jacob", surname = "K", sex = "male",
                    city = "Bedzin", category = "III", elo = 0)
                self._turnament.add_player(
                    name = "Joannah", surname = "K", sex = "female",
                    city = "Bedzin", category = "bk", elo = 0)
                self._turnament.add_player(
                    name = "Jaroslaw", surname = "Katchynsky", sex = "male",
                    city = "Nowogrodzka", category = "bk", elo = 0)
                self._turnament.add_player(
                    name = "Mateush", surname = "Morawitz", sex = "male",
                    city = "Warsaw", category = "IV", elo = 0)
                self._turnament.add_player(
                    name = "Adam", surname = "Malysh", sex = "male",
                    city = "Wisla", category = "II", elo = 1755)
                self._turnament.add_player(
                    name = "Piotr", surname = "Zyla", sex = "male",
                    city = "Zakopane", category = "V", elo = 0)
                self._turnament.add_player(
                    name = "Mario", surname = "Super", sex = "male",
                    city = "Pilsudsky Square", category = "bk", elo = 1355)
                print('[DEBUG] ROUND #1:\n')
                self._turnament.begin(rounds=6)
                self._turnament.add_result(table_nr=1, result=1.0)
                self._turnament.add_result(table_nr=2, result=1.0)
                self._turnament.add_result(table_nr=3, result=0.5)
                self._turnament.apply_round_results()
                # print(self._turnament.dump_act_results())
                # print(self._turnament.dump_players())

                print('[DEBUG] ROUND #2:\n')
                self._turnament.next_round()
                # print(self._turnament.dump())
                self._turnament.add_result(table_nr=1, result=0.5)
                self._turnament.add_result(table_nr=2, result=0.0)
                self._turnament.add_result(table_nr=3, result=1.0)
                self._turnament.apply_round_results()
                # print(self._turnament.dump_act_results())
                # print(self._turnament.dump_players())

                print('[DEBUG] ROUND #3:\n')
                self._turnament.next_round()
                # print(self._turnament.dump())
                self._turnament.add_result(table_nr=1, result=0.5)
                self._turnament.add_result(table_nr=2, result=0.0)
                self._turnament.add_result(table_nr=3, result=1.0)
                self._turnament.apply_round_results()
                # print(self._turnament.dump_act_results())
                # print(self._turnament.dump_players())

                print('[DEBUG] ROUND #4:\n')
                self._turnament.next_round()
                # print(self._turnament.dump())
                self._turnament.add_result(table_nr=1, result=0.5)
                self._turnament.add_result(table_nr=2, result=0.5)
                self._turnament.add_result(table_nr=3, result=1.0)
                self._turnament.apply_round_results()
                # print(self._turnament.dump_act_results())
                # print(self._turnament.dump_players())

                print('[DEBUG] ROUND #5:\n')
                self._turnament.next_round()
                # print(self._turnament.dump())
                self._turnament.add_result(table_nr=1, result=0.5)
                self._turnament.add_result(table_nr=2, result=-1.0)
                self._turnament.add_result(table_nr=3, result=1.0)
                self._turnament.apply_round_results()
                # print(self._turnament.dump_act_results())
                print(self._turnament.dump_players_p_o())

                print('[DEBUG] ROUND #6:\n')
                self._turnament.next_round()
                # print(self._turnament.dump())
                self._turnament.add_result(table_nr=1, result=0.5)
                self._turnament.add_result(table_nr=2, result=0.0)
                self._turnament.add_result(table_nr=3, result=0.0)
                self._turnament.apply_round_results()
                print(self._turnament.dump_act_results())
                print(self._turnament.dump_players())
            else:
                print('No turnament file selected.')
            

if __name__=="__main__":
    _comment = 'Application class. It handles init(), run() and end() methods. '
    print(_comment)


