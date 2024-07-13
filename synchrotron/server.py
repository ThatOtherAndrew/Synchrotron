from contextlib import asynccontextmanager

import uvicorn
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
    return list(map(str, return_values))


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=2031)
