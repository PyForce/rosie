import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# allow CORS on all requests
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'],
                   allow_headers=['*'])

server = None

from . import routes

if __name__ == '__main__':
    raise Exception('do not launch directly!')


def init():
    from rosie.config import config
    host = config.get('rest_api', 'host', fallback='0.0.0.0')
    port = config.getint('rest_api', 'port', fallback=5000)
    debug = config.getboolean('rest_api', 'debug', fallback=False)

    global server
    server = uvicorn.Server(uvicorn.Config(
        app, host=host, port=port, log_level='debug' if debug else 'warning'))
    server.run()


def end():
    server.should_exit = True
