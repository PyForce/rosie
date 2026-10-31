import asyncio

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import ValidationError

from rosie.apis.web import routes
from rosie.robot import Robot


async def serve(robot: Robot, host: str, port: int) -> None:
    """The web API on host:port, until cancelled."""
    server = uvicorn.Server(
        uvicorn.Config(create_app(robot), host=host, port=port, log_level="warning")
    )
    serving = asyncio.ensure_future(server.serve())
    try:
        await asyncio.shield(serving)
    except asyncio.CancelledError:
        # rosie is stopping: let uvicorn close the connections first
        server.should_exit = True
        await serving
        raise


def create_app(robot: Robot) -> FastAPI:
    """REST + WebSocket interface to `robot`."""
    app = FastAPI(title="rosie")
    # WebRosie is served from another origin than the robot
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )

    @app.exception_handler(ValidationError)
    async def invalid_request(_request: Request, error: ValidationError) -> Response:
        # error.json() also serialises raw input that isn't valid JSON (bytes)
        detail = error.json(include_url=False)
        return Response(f'{{"detail":{detail}}}', status_code=422, media_type="application/json")

    app.state.robot = robot
    app.include_router(routes.router)

    supervisor = routes.WebSupervisor(robot)
    robot.supervisor().append(supervisor)
    # bound methods can't use the decorators
    app.add_api_websocket_route("/websocket", supervisor.websocket)
    app.add_api_route("/auto_mode", supervisor.auto_mode, methods=["PUT", "POST"])
    app.add_api_route("/manual_mode", supervisor.manual_mode, methods=["PUT", "POST"])
    return app
