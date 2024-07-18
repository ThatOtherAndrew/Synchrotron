import contextlib

import uvicorn

from .server import app

if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt):
        uvicorn.run(app, host='localhost', port=2031)
