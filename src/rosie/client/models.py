import math
from dataclasses import dataclass

# steer (+1 right), throttle (+1 forward), rotation (+1 clockwise, like E), each in [-1, 1]
type Direction = tuple[float, float, float]


@dataclass(frozen=True, slots=True)
class Position:
    x: float  # m
    y: float  # m
    theta: float  # rad, counter-clockwise from the x axis

    def distance_to(self, x: float, y: float) -> float:
        return math.hypot(self.x - x, self.y - y)


@dataclass(frozen=True, slots=True)
class Metadata:
    name: str
    profile: str
    thumbnail: str  # path of the robot's picture
    vector: str  # path of the robot's icon
    video: str | None  # video stream (":port/path" on the robot's host), if any
    size: tuple[float, float, float]  # length, width, height (m)
