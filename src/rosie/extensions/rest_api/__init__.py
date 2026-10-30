import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import routes


def create_app(robot):
    """
    REST + WebSocket interface to `robot`
    """
    app = FastAPI()

    # allow CORS on all requests
    app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'],
                       allow_headers=['*'])

    app.state.robot = robot
    app.include_router(routes.router)

    supervisor = routes.RestAPIMovementSupervisor(robot)
    robot.supervisor().append(supervisor)
    # bound methods can't use the decorators
    app.add_api_websocket_route('/websocket', supervisor.websocket)
    app.add_api_route('/auto_mode', supervisor.auto_mode, methods=['PUT', 'POST'])
    app.add_api_route('/manual_mode', supervisor.manual_mode,
                      methods=['PUT', 'POST'])
    return app


async def run(robot, settings):
    host = settings.get('host', fallback='0.0.0.0')
    port = settings.getint('port', fallback=5000)
    debug = settings.getboolean('debug', fallback=False)

    server = uvicorn.Server(uvicorn.Config(
        create_app(robot), host=host, port=port,
        log_level='debug' if debug else 'warning'))
    serving = asyncio.ensure_future(server.serve())
    try:
        await asyncio.shield(serving)
    except asyncio.CancelledError:
        # rosie is stopping: let uvicorn close the connections first
        server.should_exit = True
        await serving
        raise
