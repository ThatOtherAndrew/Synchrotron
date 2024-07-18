from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from synchrotron import Synchrotron

from . import api
from .dependencies import SynchrotronDependency


# noinspection PyUnresolvedReferences
@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    fastapi_app.state.synchrotron = Synchrotron()
    yield
    fastapi_app.state.synchrotron.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(api.router)


@app.get('/')
async def root():
    return 'Synchrotron server running'


@app.get('/execute')
async def execute(request: Request, synchrotron: SynchrotronDependency) -> str:
    body = await request.body()
    return_values = synchrotron.execute(body.decode())
    return repr(return_values)
