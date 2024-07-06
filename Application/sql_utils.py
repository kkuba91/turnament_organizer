"""sql_utils.py

    SQL Alchemy util methods for data read/write to static memory.
    Here preferred logging level is DEBUG only.

"""
# Global package imports:
import logging
from dataclasses import dataclass
from sqlalchemy import (MetaData, Table, Column, Integer, String, Date, inspect, Boolean,
                        bindparam, select, Float)

# Local package imports:
from Application.logger import log_method

TURNAMENT_TABLE_COLS = [
    Column('_Id', Integer, primary_key=True, nullable=False),
    Column('Name', String),
    Column('Place', String),
    Column('RoundActual', Integer),
    Column('RoundFinished', Integer),
    Column('Rounds', Integer),
    Column('DateStart', Date),
    Column('DateEnd', Date),
    Column('System', Integer),
    Column('Finished', Boolean)
]

PLAYERS_TABLE_COLS = [
    Column('_Id', Integer, primary_key=True, nullable=False),
    Column('Nr', Integer),
    Column('Name', String),
    Column('Surname', String),
    Column('Sex', String),
    Column('City', String),
    Column('Club', String),
    Column('Birth', Date),
    Column('Category', String),
    Column('Elo', Integer),
    Column('Elo_rapid', Integer),
    Column('Elo_blitz', Integer)
]

RESULTS_TABLE_COLS = [
    Column('_Id', Integer, primary_key=True, nullable=False),
    Column('Round', Integer),
    Column('Table', Integer),
    Column('Player_w', Integer),
    Column('Player_b', Integer),
    Column('Result', Float)
]


class SqlUtils(object):
    @dataclass
    class DbElements:
        turnament = None
        players = None
        results = None

    def __init__(self, engine) -> None:
        self.engine = engine
        self.meta_data = MetaData(engine)
        self.db = SqlUtils.DbElements()
        self.connection = self.engine.connect()

    def turnament_init(self):
        table_name = "Turnament"
        log_method(self, self.turnament_init)
        self.db.turnament = \
            self._sql_init_table_or_get_existing(table_name=table_name,
                                                 table_cols=TURNAMENT_TABLE_COLS)
        self.players_init()
        self.results_init()

    def get_turnament_info(self):
        table_name = "Turnament"
        log_method(self, self.get_turnament_info)
        self.db.turnament = self._get_table_info(table_name=table_name,
                                                 db_table=self.db.turnament)

    def update_turnament_info(self, **kwargs):
        table_name = "Turnament"
        log_method(self, self.update_turnament_info)
        if table_name not in inspect(self.engine).get_table_names():
            logging.error(f"No table \"{table_name}\"!")
            return {}
        data = {'_Id': 1}
        bind_data = {}
        logging.debug(f"kwargs: {kwargs}")
        for col in TURNAMENT_TABLE_COLS:
            if not col.primary_key and kwargs.get(str(col.key).lower()):
                data[str(col.key)] = kwargs[str(col.key).lower()]
                bind_data[str(col.key)] = bindparam(str(col.key))
        logging.debug(f"data: {data}")

        # Check table is empty
        if self.connection.execute(select([self.db.turnament])).fetchall():
            stmt = self.db.turnament.update().where(self.db.turnament.c._Id == 1). \
                values(bind_data)
            logging.debug(f"Updating table \"{table_name}\"")
        else:
            stmt = self.db.turnament.insert()
            logging.debug(f"Inserting into table \"{table_name}\"")
        self.engine.execute(stmt, [data, ])

    def read_turnament_info(self, **kwargs):
        table_name = "Turnament"
        log_method(self, self.read_turnament_info)
        if table_name not in inspect(self.engine).get_table_names():
            logging.error(f"No table \"{table_name}\"!")
            return {}
        results = self._get_table_data(table_name=table_name,
                                       db_table=self.db.turnament,
                                       table_cols=TURNAMENT_TABLE_COLS)
        logging.debug(f"Reading general info from table \"{table_name}\":\n{results}")
        return results

    def players_init(self):
        table_name = "Players"
        log_method(self, self.players_init)
        self.db.players = \
            self._sql_init_table_or_get_existing(table_name=table_name,
                                                 table_cols=PLAYERS_TABLE_COLS)

    def get_players_info(self):
        table_name = "Players"
        log_method(self, self.get_players_info)
        self.db.players = self._get_table_info(table_name=table_name,
                                               db_table=self.db.players)

    def update_player_info(self, **kwargs):
        table_name = "Players"
        name = kwargs.get("name")
        surname = kwargs.get("surname")
        log_method(self, self.update_player_info)
        if table_name not in inspect(self.engine).get_table_names():
            logging.error(f"No table \"{table_name}\"!")
            return {}
        data = {}
        bind_data = {}
        logging.debug(f"kwargs: {kwargs}")
        for col in PLAYERS_TABLE_COLS:
            if not col.primary_key and kwargs.get(str(col.key).lower()):
                data[str(col.key)] = kwargs[str(col.key).lower()]
                bind_data[str(col.key)] = bindparam(str(col.key))
        logging.debug(f"data: {data}")

        # Check table is empty
        if self.connection.execute(select([self.db.players])).fetchall():
            stmt = self.db.players.update().where(self.db.players.c.Name == name). \
                where(self.db.players.c.Surname == surname).values(bind_data)
            logging.debug(f"Updating player {name} {surname}")
            self.engine.execute(stmt, [data, ])
        else:
            raise Exception("No players added yet!")

    def remove_player_info(self, **kwargs):
        table_name = "Players"
        name = kwargs.get("name")
        surname = kwargs.get("surname")
        log_method(self, self.update_player_info)
        if table_name not in inspect(self.engine).get_table_names():
            logging.error(f"No table \"{table_name}\"!")
            return {}

        # Check table is empty
        if self.connection.execute(select([self.db.players])).fetchall():
            stmt = self.db.players.delete().where(self.db.players.c.Name == name). \
                where(self.db.players.c.Surname == surname)
            logging.debug(f"Deleting player {name} {surname}")
            self.engine.execute(stmt)
        else:
            raise Exception("No players added yet!")

    def insert_player_info(self, **kwargs):
        table_name = "Players"
        name = kwargs.get("name")
        surname = kwargs.get("surname")
        log_method(self, self.insert_player_info)
        if table_name not in inspect(self.engine).get_table_names():
            logging.error(f"No table \"{table_name}\"!")
            return {}
        data = {}
        bind_data = {}
        logging.debug(f"kwargs: {kwargs}")
        for col in PLAYERS_TABLE_COLS:
            if not col.primary_key and kwargs.get(str(col.key).lower()):
                data[str(col.key)] = kwargs[str(col.key).lower()]
                bind_data[str(col.key)] = bindparam(str(col.key))
        logging.debug(f"data: {data}")

        stmt = self.db.players.insert()
        logging.debug(f"Inserting {name} {surname} into table \"{table_name}\"")
        self.engine.execute(stmt, [data, ])

    def read_players_info(self, **kwargs):
        table_name = "Players"
        log_method(self, self.read_players_info)
        if table_name not in inspect(self.engine).get_table_names():
            logging.error(f"No table \"{table_name}\"!")
            return {}
        players = self._get_table_data(table_name=table_name,
                                       db_table=self.db.players,
                                       table_cols=PLAYERS_TABLE_COLS)
        self._replace_None(list_of_dicts=players, key_names=['city', 'club'], replace_to="")
        logging.debug(f"Reading Players from table \"{table_name}\":\n{players}")
        return players
    
    @staticmethod
    def _replace_None(list_of_dicts: list, key_names: list, replace_to: any) -> list:
        for element in list_of_dicts:
            for key_name in key_names:
                if key_name in element:
                    element[key_name] = replace_to
        return list_of_dicts


    def results_init(self):
        table_name = "Results"
        log_method(self, self.results_init)
        self.db.results = \
            self._sql_init_table_or_get_existing(table_name=table_name,
                                                 table_cols=RESULTS_TABLE_COLS)

    def insert_result(self, **kwargs):
        table_name = "Results"
        log_method(self, self.insert_result)
        if table_name not in inspect(self.engine).get_table_names():
            logging.error(f"No table \"{table_name}\"!")
            return {}
        data = {}
        logging.debug(f"kwargs: {kwargs}")
        data['Round'] = kwargs.get("round")
        data['Table'] = kwargs.get("table")
        data['Player_w'] = kwargs.get("player_w")
        data['Player_b'] = kwargs.get("player_b")
        data['Result'] = kwargs.get("result")

        act_results = self._get_table_data(table_name=table_name,
                                           db_table=self.db.results,
                                           table_cols=RESULTS_TABLE_COLS)
        if any([data["Round"] == act["round"] and data["Table"] == act["table"] for act in act_results]):
            stmt_update = self.db.results.update().where(self.db.results.c.Round == data['Round']). \
                where(self.db.results.c.Table == data['Table']).values(data)
            self.engine.execute(stmt_update, [data, ])
            logging.debug(f"Updateing {kwargs} into table \"{table_name}\"")
        else:
            stmt_insert = self.db.results.insert()
            self.engine.execute(stmt_insert, [data, ])
            logging.debug(f"Inserting {kwargs} into table \"{table_name}\"")

    def read_results_info(self, **kwargs):
        table_name = "Results"
        log_method(self, self.read_results_info)
        if table_name not in inspect(self.engine).get_table_names():
            logging.error(f"No table \"{table_name}\"!")
            return {}
        results = self._get_table_data(table_name=table_name,
                                       db_table=self.db.results,
                                       table_cols=RESULTS_TABLE_COLS)
        logging.debug(f"Reading Results from table \"{table_name}\":\n{results}")
        return results

    def _sql_init_table_or_get_existing(self,
                                        table_name: str,
                                        table_cols: list):
        log_method(self, self._sql_init_table_or_get_existing)
        self.engine.connect()
        self.meta_data.reflect(bind=self.engine)
        if table_name not in inspect(self.engine).get_table_names():
            logging.debug(f"Creating new table: \"{table_name}\"")
            db_table = Table(table_name, self.meta_data,
                             *table_cols)
            self.meta_data.create_all()
        else:
            logging.debug(f"Getting existing table: \"{table_name}\"")
            db_table = self.meta_data.tables[table_name]
            logging.debug(f"{db_table}")
            db_table = self._get_table_info(table_name=table_name, db_table=db_table)
        return db_table

    def _get_table_info(self, table_name, db_table):
        log_method(self, self._get_table_info)
        if table_name not in inspect(self.engine).get_table_names():
            logging.error(f"No table \"{table_name}\"!")
            return {}
        result = self.connection.execute(select([db_table]))
        logging.debug(f"result: {result.fetchall()}")
        return db_table

    def _get_table_data(self, table_name, db_table, table_cols):
        log_method(self, self._get_table_data)
        if table_name not in inspect(self.engine).get_table_names():
            logging.error(f"No table \"{table_name}\"!")
            return {}
        result = self.connection.execute(select([db_table])).fetchall()
        data_rows = []
        for row_tuple in result:
            row = {}
            col_nr = 0
            for col in table_cols:
                row[str(col.key).lower()] = row_tuple[col_nr]
                col_nr += 1
            data_rows.append(row)
        return data_rows
