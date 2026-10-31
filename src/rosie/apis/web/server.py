import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import ValidationError

from rosie.apis.web import routes
from rosie.core import Robot
from rosie.models import Settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def start_web_api(robot: Robot, settings: Settings) -> AsyncGenerator[None, None]:
    """Start the web API; on the way out of the block, uvicorn closes its connections."""
    server = uvicorn.Server(
        uvicorn.Config(
            create_app(robot), host=settings.host, port=settings.port, log_level="warning"
        )
    )
    serving = asyncio.create_task(server.serve())
    logger.info("web API on http://%s:%d", settings.host, settings.port)
    try:
        yield
    finally:
        server.should_exit = True
        await serving


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
