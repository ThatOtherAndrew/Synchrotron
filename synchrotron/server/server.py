from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from synchrotron import Synchrotron


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    fastapi_app.state.synchrotron = Synchrotron()
    yield
    fastapi_app.state.synchrotron.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get('/')
async def root():
    return 'Synchrotron server running'


@app.get('/execute')
async def execute(request: Request):
    body = await request.body()
    synchrotron: Synchrotron = app.state.synchrotron
    return_values = synchrotron.execute(body.decode())
    return return_values
