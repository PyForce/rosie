from typing import Literal

from pydantic import BaseModel, ConfigDict


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)


class Position(_Frozen):
    x: float  # m
    y: float  # m
    theta: float  # rad


class GotoOrder(_Frozen):
    target: tuple[float, float]  # x, y (m)
    speed: float  # m/s
    planner: bool = False  # go around walls and furniture


class FollowOrder(_Frozen):
    path: list[tuple[float, float]]  # points to drive through (m)
    speed: float  # m/s


class RobotInfo(_Frozen):
    name: str
    thumbnail: str  # path of the robot's picture
    vector: str  # path of the robot's icon
    video: str | Literal[False]  # video stream (":port/path" on the robot's host), if any
    size: tuple[float, float, float]  # length, width, height (m)
    profile: str


class Maps(_Frozen):
    maps: list[str]


class DriveCommand(_Frozen):
    """WebSocket, client to rosie: the driving commands under manual control."""

    type: Literal["move"]
    data: tuple[float, float, float]  # steering, throttle, spin, each in [-1, 1]


class PositionUpdate(_Frozen):
    """WebSocket, rosie to clients: where the robot is now."""

    type: Literal["position"]
    data: Position
