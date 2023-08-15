"""api.py

    Concurrent, next to cli, form of application control.

"""
# Global package imports:
import asyncio
from enum import Enum
import logging

# Local package imports:
from Resources import __version__, APPLICATION_NAME

# Third Party packages:
from fastapi import FastAPI, APIRouter
import uvicorn

api = FastAPI(title="Chess turnament manager",
              description="Swiss, single elimination, circular systems",
              version=__version__)

class ApiData:

    class Tags:

        app = "General"
        turnament = "Turnament"
        rounds = "Round"

    def __init__(self, **kwargs) -> None:
        self.routers = {}
        self.api = api
        if hasattr(kwargs, "debug"):
            self.api.debug = kwargs.get("debug")
        if not isinstance(self.api, FastAPI):
            raise TypeError("No API (FastAPI) object.")
        self.app = kwargs.get('app')
        if not isinstance(self.app, object):
            raise TypeError("No APP object for API.")
        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.propagate = False
        self._init_endpoints()
        

    def run_api(self):
        """
        Start API app.
        """
        kwargs = {
            'app': self.api,
            'port': 8000,
            'loop': 'asyncio'
        }
        uvicorn.run(**kwargs)

    @api.get("/", include_in_schema=False)
    async def init() -> dict:
        data = {'name': APPLICATION_NAME, 'version': __version__}
        return data
        

    def _init_endpoints(self):
        # App general:
        tag = self.Tags.app
        self.routers[tag] = APIRouter()
        self.routers[tag].add_api_route(path="/",
                                        endpoint=self.app_info,
                                        methods=["GET"],
                                        description="Get application version",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/get_status",
                                        endpoint=self.app_status,
                                        methods=["GET"],
                                        description="Get app status about turnament processing",
                                        tags=[tag])
        self.api.include_router(self.routers[tag], prefix="/{}".format(tag))
        
        # Turnament:
        tag = self.Tags.turnament
        self.routers[tag] = APIRouter()
        self.routers[tag].add_api_route(path="/create",
                                        endpoint=self.create_turnament,
                                        methods=["POST"],
                                        description="Create new turnament file and open the instance",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/open",
                                        endpoint=self.open_turnament,
                                        methods=["POST"],
                                        description="Open existing turnament instance from file",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/start",
                                        endpoint=self.start_turnament,
                                        methods=["POST"],
                                        description="Start first round",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/save",
                                        endpoint=self.save_turnament,
                                        methods=["POST"],
                                        description="Save turnament state",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/load",
                                        endpoint=self.load_turnament,
                                        methods=["POST"],
                                        description="Load last saved turnament state",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/finish",
                                        endpoint=self.finish_turnament,
                                        methods=["POST"],
                                        description="Finish actual turnament at current round",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/close",
                                        endpoint=self.close_turnament,
                                        methods=["POST"],
                                        description="Close actual turnament instance",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/player/add",
                                        endpoint=self.turnament_player_add,
                                        methods=["POST"],
                                        description="Add Player",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/player/del",
                                        endpoint=self.turnament_player_del,
                                        methods=["POST"],
                                        description="Remove Player",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/players",
                                        endpoint=self.turnament_players,
                                        methods=["GET"],
                                        description="Get Player list",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/results",
                                        endpoint=self.turnament_results,
                                        methods=["GET"],
                                        description="Get results",
                                        tags=[tag])
        self.api.include_router(self.routers[tag], prefix="/{}".format(tag))

        # Round:
        tag = self.Tags.rounds
        self.routers[tag] = APIRouter()
        self.routers[tag].add_api_route(path="/turnament/round",
                                        endpoint=self.turnament_round,
                                        methods=["GET"],
                                        description="Get round data",
                                        tags=[tag])
        self.api.include_router(self.routers[tag], prefix="/{}".format(tag))

    # Endpoint methods:
    # @TAG: "App general"
    def app_info(self):
        logging.info('[API] Get general application information')
        return self.app.actions.app_info()

    def app_status(self):
        logging.info('[API] Get application status')
        return self.app.actions.app_status()

    # @TAG: "Turnament"
    async def create_turnament(self, name: str):
        await asyncio.sleep(0.01)
        logging.info('[API]: Creating turnament with name: {} ..'.format(name))
        return self.app.actions.open(name=name, cmd="New")

    async def open_turnament(self, name: str):
        await asyncio.sleep(0.01)
        logging.info('[API]: Opening turnament with name: {} ..'.format(name))
        return self.app.actions.open(name=name, cmd="Open")
    
    async def start_turnament(self, rounds: int, system_type: str):
        await asyncio.sleep(0.01)
        logging.info('[API]: Starting actual turnament. Rounds: {}. System: {} ..'
                     .format(rounds, system_type))
        return self.app.actions.turnament_start(rounds=rounds, system_type=system_type)
    
    async def save_turnament(self):
        await asyncio.sleep(0.01)
        logging.info('[API]: Saving state of actual turnament ..')
        raise NotImplementedError
    
    async def load_turnament(self):
        await asyncio.sleep(0.01)
        logging.info('[API]: Loading last state of actual turnament ..')
        raise NotImplementedError
    
    async def finish_turnament(self):
        await asyncio.sleep(0.01)
        logging.info('[API]: Finishing actual turnament ..')
        raise NotImplementedError
    
    async def close_turnament(self):
        await asyncio.sleep(0.01)
        logging.info('[API]: Closing actual turnament instance ..')
        raise NotImplementedError

    async def turnament_player_add(self,
                                   name: str,
                                   surname: str,
                                   sex="male",
                                   city="",
                                   category="bk",
                                   elo=0):
        await asyncio.sleep(0.01)
        logging.info('[API]: Add Player: {} ..'.format(name))
        return self.app.actions.player_add(name=name,
                                           surname=surname,
                                           sex=sex,
                                           city=city,
                                           category=category,
                                           elo=elo)

    async def turnament_player_del(self,
                                   name: str,
                                   surname=""):
        await asyncio.sleep(0.01)
        logging.info('[API]: Remove Player: {} ..'.format(name))
        return self.app.actions.player_del(name=name,
                                           surname=surname)
    
    async def turnament_players(self,
                                type: str):
        await asyncio.sleep(0.01)
        logging.info(f'[API]: Get Player list for "{type}" ..')
        return self.app.actions.players_get(type=type)


    async def turnament_results(self):
        await asyncio.sleep(0.01)
        logging.info('[API]: Get results ..')
        return self.app.actions.turnament_results()

    # @TAG: "Round"
    async def turnament_round(self, nr=0):
        await asyncio.sleep(0.01)
        logging.info('[API]: Get round data ..')
        return self.app.actions.turnament_round(nr=nr)
    
    async def set_round_result(self, table_nr: int, result: int):
        await asyncio.sleep(0.01)
        logging.info('[API]: Set round result ..')
        return self.app.actions.turnament_round(nr=nr)
