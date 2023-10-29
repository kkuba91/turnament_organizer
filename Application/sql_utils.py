"""sql_utils.py

    SQL Alchemy util methods for data read/write to static memory.
    Here preferred logging level is DEBUG only.

"""
# Global package imports:
import logging
from dataclasses import dataclass
from sqlalchemy import (MetaData, Table, Column, Integer, String, Date, inspect,
                        bindparam, select)

# Local package imports:
from Application.logger import log_method

TURNAMENT_TABLE_COLS = [
    Column('_Id', Integer, primary_key=True, nullable=False),
    Column('Name', String),
    Column('Place', String),
    Column('RoundActual', Integer),
    Column('Rounds', Integer),
    Column('DateStart', Date),
    Column('DateEnd', Date),
    Column('System', Integer)
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


class SqlUtils(object):
    @dataclass
    class DbElements:
        turnament = None
        players = None
        rounds = None

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
        if kwargs.get('name'):
            data['Name'] = kwargs['name']
            bind_data['Name'] = bindparam('Name')
        if kwargs.get('place'):
            data['Place'] = kwargs['place']
            bind_data['Place'] = bindparam('Place')
        if kwargs.get('round_actual'):
            data['RoundActual'] = kwargs['round_actual']
            bind_data['RoundActual'] = bindparam('RoundActual')
        if kwargs.get('rounds'):
            data['Rounds'] = kwargs['rounds']
            bind_data['Rounds'] = bindparam('Rounds')
        if kwargs.get('date_start'):
            data['DateStart'] = kwargs['date_start']
            bind_data['DateStart'] = bindparam('DateStart')
        if kwargs.get('date_end'):
            data['DateEnd'] = kwargs['date_end']
            bind_data['DateEnd'] = bindparam('DateEnd')
        if kwargs.get('system'):
            data['System'] = kwargs['system']
            bind_data['System'] = bindparam('System')
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
        data = {}

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
