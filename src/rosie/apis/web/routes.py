import asyncio
import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import ValidationError

from rosie.apis.web.models import Follow, Goto, Maps, Metadata, Move, Position, PositionUpdate
from rosie.errors import NoRouteError
from rosie.motion.models import RobotState
from rosie.motion.supervisors import MovementSupervisor
from rosie.robot import Robot

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
def metadata(request: Request, robot: RobotDependency) -> Metadata:
    profile = robot.profile
    return Metadata(
        name=profile.name,
        thumbnail=request.app.url_path_for("thumbnail"),
        vector=request.app.url_path_for("vector"),
        video=profile.video or False,
        size=(profile.body.length, profile.body.width, profile.body.height),
        profile=profile.id,
    )


@router.get("/thumbnail")
def thumbnail(robot: RobotDependency) -> FileResponse:
    return FileResponse(robot.profile.thumbnail)


@router.get("/vector")
def vector(robot: RobotDependency) -> FileResponse:
    return FileResponse(robot.profile.vector)


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
    order = Goto.model_validate_json(await request.body())
    x, y, t = order.target
    try:
        if order.planner:
            robot.go_to_with_planner(x, y, t)
        else:
            robot.go_to(x, y, t)
    except NoRouteError as error:
        return JSONResponse({"error": str(error)}, status_code=409)
    except ValueError as error:
        return JSONResponse({"detail": str(error)}, status_code=422)
    return Response()


@router.post("/follow")
async def follow(request: Request, robot: RobotDependency) -> Response:
    order = Follow.model_validate_json(await request.body())
    try:
        robot.follow(order.path, order.time)
    except ValueError as error:
        return JSONResponse({"detail": str(error)}, status_code=422)
    return Response()


@router.get("/maps")
def maps(robot: RobotDependency) -> Maps:
    return Maps(maps=list(robot.maps()))


@router.get("/map")
@router.get("/map/{name}")
def getmap(robot: RobotDependency, name: str = "") -> dict[str, Any]:
    worldmap = robot.get_map(name)
    if not worldmap:
        raise HTTPException(status_code=404)
    return worldmap


class WebSupervisor(MovementSupervisor):
    """Streams the robot's position to WebSocket clients and takes their keys in manual mode."""

    def __init__(self, robot: Robot) -> None:
        self.robot = robot
        self.manual = False
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

    def movement_update(self, robot_state: RobotState) -> None:
        pose = robot_state.pose
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

    def manual_mode(self) -> Response:
        self.manual = True
        self.robot.start_open_loop_control()
        return Response()

    def auto_mode(self) -> Response:
        self.manual = False
        self.robot.stop_open_loop_control()
        return Response()

    def _receive(self, text: str) -> None:
        message = json.loads(text)
        if not isinstance(message, dict) or message.get("type") != "move" or not self.manual:
            return
        try:
            move = Move.model_validate(message)
        except ValidationError:
            logger.warning("ignoring malformed move: %s", text)
            return
        self.robot.add_movement(list(move.data))

    def _sent(self, task: asyncio.Task[None]) -> None:
        """Forget a finished send; a client gone meanwhile is not an error."""
        self.sending.discard(task)
        if not task.cancelled():
            task.exception()
