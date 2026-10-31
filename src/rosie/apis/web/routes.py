import asyncio
import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import ValidationError

from rosie.apis.web.models import (
    DriveCommand,
    FollowOrder,
    GotoOrder,
    Maps,
    Position,
    PositionUpdate,
    RobotInfo,
)
from rosie.control.models import Telemetry
from rosie.core import Robot
from rosie.errors import NoRouteError

logger = logging.getLogger(__name__)

router = APIRouter()


def get_robot(request: Request) -> Robot:
    robot: Robot = request.app.state.robot
    return robot


RobotDependency = Annotated[Robot, Depends(get_robot)]


@router.get("/odometry")
def odometry(robot: RobotDependency) -> Position:
    x, y, theta = robot.position()
    return Position(x=x, y=y, theta=theta)


@router.get("/metadata")
def metadata(request: Request, robot: RobotDependency) -> RobotInfo:
    profile = robot.profile
    return RobotInfo(
        name=profile.name,
        thumbnail=request.app.url_path_for("thumbnail"),
        vector=request.app.url_path_for("vector"),
        video=profile.camera.stream if profile.camera else False,
        size=(profile.body.length, profile.body.width, profile.body.height),
        profile=profile.folder_name,
    )


@router.get("/thumbnail")
def thumbnail(robot: RobotDependency) -> FileResponse:
    return FileResponse(robot.profile.picture)


@router.get("/vector")
def vector(robot: RobotDependency) -> FileResponse:
    return FileResponse(robot.profile.icon)


@router.get("/sensor/{name}")
def sensor(name: str, robot: RobotDependency) -> dict[str, object]:
    if name not in robot.sensors:
        raise HTTPException(status_code=404, detail=f"no sensor {name}")
    return {name: robot.sensors[name]()}


@router.post("/position")
async def position(request: Request, robot: RobotDependency) -> Response:
    """Teleport the robot."""
    target = Position.model_validate_json(await request.body())
    robot.teleport(target.x, target.y, target.theta)
    return Response()


@router.post("/goto")
async def goto(request: Request, robot: RobotDependency) -> Response:
    order = GotoOrder.model_validate_json(await request.body())
    x, y, t = order.target
    try:
        if order.planner:
            robot.goto_with_planner(x, y, t)
        else:
            robot.goto(x, y, t)
    except NoRouteError as error:
        return JSONResponse({"error": str(error)}, status_code=409)
    except ValueError as error:
        return JSONResponse({"detail": str(error)}, status_code=422)
    return Response()


@router.post("/follow")
async def follow(request: Request, robot: RobotDependency) -> Response:
    order = FollowOrder.model_validate_json(await request.body())
    try:
        robot.follow(order.path, order.time)
    except ValueError as error:
        return JSONResponse({"detail": str(error)}, status_code=422)
    return Response()


@router.get("/maps")
def maps(robot: RobotDependency) -> Maps:
    return Maps(maps=list(robot.maps()))


@router.get("/map")
def current_map(robot: RobotDependency) -> dict[str, Any]:
    """The map the planner uses."""
    worldmap = robot.get_map(robot.map_name) if robot.map_name else None
    if not worldmap:
        raise HTTPException(status_code=404)
    return worldmap


@router.get("/map/{name}")
def getmap(name: str, robot: RobotDependency) -> dict[str, Any]:
    worldmap = robot.get_map(name)
    if not worldmap:
        raise HTTPException(status_code=404)
    return worldmap


@router.post("/map/{name}")
def use_map(name: str, robot: RobotDependency) -> Response:
    """Plan routes on this map from now on."""
    if name not in robot.maps():
        raise HTTPException(status_code=404, detail=f"no map {name}")
    robot.use_map(name)
    return Response()


class WebObserver:
    """Streams the robot's position to WebSocket clients, and takes their commands in manual mode."""

    def __init__(self, robot: Robot) -> None:
        self.robot = robot
        self.is_manual = False
        self.clients: list[WebSocket] = []
        # pending sends, kept until done (the event loop only keeps weak references)
        self.sending: set[asyncio.Task[None]] = set()
        self.last_location = (0.0, 0.0, 0.0)

    async def websocket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        logger.debug("connected websocket client: %s", websocket.client)
        self.clients.append(websocket)
        try:
            while True:
                self._receive(await websocket.receive_text())
        except WebSocketDisconnect:
            pass
        finally:
            self.clients.remove(websocket)

    def movement_begin(self, expected_updates: int | None) -> None:
        pass

    def movement_end(self) -> None:
        pass

    def movement_update(self, telemetry: Telemetry) -> None:
        pose = telemetry.pose
        location = (pose.x, pose.y, pose.theta)
        if location == self.last_location:
            return
        self.last_location = location

        message = PositionUpdate(
            type="position", data=Position(x=pose.x, y=pose.y, theta=pose.theta)
        ).model_dump_json()
        for client in list(self.clients):
            task = asyncio.create_task(client.send_text(message))
            self.sending.add(task)
            task.add_done_callback(self._sent)

    def manual(self) -> Response:
        self.is_manual = True
        self.robot.start_manual()
        return Response()

    def planned(self) -> Response:
        self.is_manual = False
        self.robot.stop_manual()
        return Response()

    def _receive(self, text: str) -> None:
        message = json.loads(text)
        if not isinstance(message, dict) or message.get("type") != "move" or not self.is_manual:
            return
        try:
            move = DriveCommand.model_validate(message)
        except ValidationError:
            logger.warning("ignoring malformed move: %s", text)
            return
        steering, throttle, spin = move.data
        self.robot.move(steering, throttle, spin)

    def _sent(self, task: asyncio.Task[None]) -> None:
        """Forget a finished send; a client gone meanwhile is not an error."""
        self.sending.discard(task)
        if not task.cancelled():
            task.exception()
