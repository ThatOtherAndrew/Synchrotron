from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from synchrotron.synchrotron import Synchrotron

from . import api


# noinspection PyUnresolvedReferences
@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    fastapi_app.state.synchrotron = Synchrotron()
    yield
    fastapi_app.state.synchrotron.shutdown()


app = FastAPI(lifespan=lifespan)
# noinspection PyTypeChecker
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
app.include_router(api.router)


@app.get('/')
async def root():
    return 'Synchrotron server running'
