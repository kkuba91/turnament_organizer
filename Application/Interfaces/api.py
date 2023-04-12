"""api.py

    Concurrent, next to cli, form of application control.

"""
# Global package imports:
import asyncio
from enum import Enum
import logging

# Local package imports:
from Resources import __version__

# Third Party packages:
from fastapi import FastAPI, APIRouter
import uvicorn

api = FastAPI(title="Chess turnament manager",
              description="Swiss, single elimination, circular systems",
              version=__version__)

class ApiData:

    class Tags:

        app = "General"
        turnament = "Turnamnent"

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
        

    def _init_endpoints(self):
        # App general:
        tag = self.Tags.app
        self.routers[tag] = APIRouter()
        self.routers[tag].add_api_route(path="/general_info",
                                                  endpoint=self.app_info,
                                                  methods=["GET"],
                                                  description="Create new turnament base file",
                                                  tags=[tag])
        self.routers[tag].add_api_route(path="/get_status",
                                                  endpoint=self.app_status,
                                                  methods=["GET"],
                                                  description="Get app status about turnamnent processing",
                                                  tags=[tag])
        self.api.include_router(self.routers[tag], prefix="/{}".format(tag))
        
        # Turnament:
        tag = self.Tags.turnament
        self.routers[tag] = APIRouter()
        self.routers[tag].add_api_route(path="/create",
                                                        endpoint=self.create_turnament,
                                                        methods=["POST"],
                                                        description="Create new turnament base file",
                                                        tags=[tag])
        self.routers[tag].add_api_route(path="/open",
                                                        endpoint=self.open_turnament,
                                                        methods=["POST"],
                                                        description="Open existing turnament base file",
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
    
    async def start_turnament(self, name: str):
        await asyncio.sleep(0.01)
        logging.info('[API]: Starting turnament with name: {} ..'.format(name))
        

