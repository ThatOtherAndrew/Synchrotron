import uvicorn

from .server import app

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=2031)
