"""api.py

    Concurrent, next to cli, form of application control.

"""
# Global package imports:
import asyncio
import logging
import os

# Local package imports:
from Application.logger import CustomFormatter, set_fastapi_logging
from Resources import __version__

# Third Party packages:
from fastapi import FastAPI, APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

templates = Jinja2Templates(directory="Templates") 

api = FastAPI(title="Chess turnament manager",
              description="Swiss, single elimination, circular systems",
              version=__version__)


@api.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    for handler in logger.handlers:
        handler.setFormatter(CustomFormatter())


class ApiData:

    class Tags:

        app = "General"
        turnament = "Turnament"
        rounds = "Round"

    def __init__(self, **kwargs) -> None:
        self.routers = {}
        self.port = kwargs.get("port", 8000)
        self.api = api
        self.api.debug = kwargs.get("debug", False)
        if not isinstance(self.api, FastAPI):
            raise TypeError("No API (FastAPI) object.")
        self.app = kwargs.get('app')
        if not isinstance(self.app, object):
            raise TypeError("No APP object for API.")
        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.propagate = False
        set_fastapi_logging(debug=bool(self.api.debug))
        self._init_endpoints()

    def run_api(self):
        """
        Start API app.
        """
        kwargs = {
            'app': self.api,
            'port': self.port,
            'loop': 'asyncio'
        }
        uvicorn.run(**kwargs)

    @staticmethod
    @api.get(path="/", include_in_schema=False)
    async def init(request: Request):
        api.mount("/", StaticFiles(directory=f"{os.getcwd()}{os.sep}Templates{os.sep}Styles"), name="static")
        return templates.TemplateResponse("home.html", {"request": request})

    def _init_endpoints(self):
        # App general:
        tag = self.Tags.app
        self.routers[tag] = APIRouter()
        self.routers[tag].add_api_route(path="/",
                                        endpoint=self.app_info,
                                        methods=["GET"],
                                        description="Get application version",
                                        tags=[tag],
                                        )
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
        self.routers[tag].add_api_route(path="/get_files",
                                        endpoint=self.get_files,
                                        methods=["POST"],
                                        description="Get tournament files list",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/remove_file",
                                        endpoint=self.remove_files,
                                        methods=["POST"],
                                        description="Remove selected tournament files",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/close",
                                        endpoint=self.close_turnament,
                                        methods=["POST"],
                                        description="Close actual turnament instance",
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
        self.routers[tag].add_api_route(path="/turnament/round/get_results",
                                        endpoint=self.turnament_round,
                                        methods=["GET"],
                                        description="Get round data",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/round/get_results/html",
                                        endpoint=self.turnament_round_html,
                                        methods=["GET"],
                                        description="Get round data in static html",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/round/set_result",
                                        endpoint=self.set_round_result,
                                        methods=["POST"],
                                        description="Set round result",
                                        tags=[tag])
        self.routers[tag].add_api_route(path="/turnament/round/apply_results",
                                        endpoint=self.apply_round,
                                        methods=["POST"],
                                        description="Apply round results",
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
    async def create_turnament(self, name: str, path: str = ""):
        await asyncio.sleep(0.01)
        logging.info('[API]: Creating turnament with name: {} ..'.format(name))
        return self.app.actions.open(name=name, cmd="New", path=path)
    
    async def close_turnament(self):
        await asyncio.sleep(0.01)
        logging.info('[API]: Closing turnament ..')
        return self.app.actions.close()

    async def get_files(self, path: str = ""):
        await asyncio.sleep(0.01)
        logging.info('[API]: Get tournament files: ..')
        return self.app.actions.get_files(path=path)
    
    async def remove_files(self, tournament_name: str = ""):
        await asyncio.sleep(0.01)
        logging.info('[API]: Remove tournament files: ..')
        return self.app.actions.remove_files(tournament_name=tournament_name)
    
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

    async def turnament_player_add(self,
                                   name: str,
                                   surname: str,
                                   sex="male",
                                   city="",
                                   category="wc",
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
    async def turnament_round(self, nr=0, full=True):
        await asyncio.sleep(0.01)
        logging.info('[API]: Get round data ..')
        return self.app.actions.turnament_round(nr=nr, full=full)
    
    async def turnament_round_html(self, nr=0, full=True):
        await asyncio.sleep(0.01)
        logging.info('[API]: Get round data in html ..')
        return self.app.actions.turnament_round_to_html(nr=nr, full=full)
    
    async def set_round_result(self, table_nr: int, result: float):
        await asyncio.sleep(0.01)
        logging.info('[API]: Set round result ..')
        return self.app.actions.set_round_result(table_nr=table_nr, result=result)

    async def apply_round(self):
        await asyncio.sleep(0.01)
        logging.info('[API]: Apply round result ..')
        return self.app.actions.apply_round()
