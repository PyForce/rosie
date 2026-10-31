from collections.abc import Callable
from dataclasses import dataclass

from shapely.geometry import MultiPolygon, Polygon

from rosie.models import Pose, Velocity
from rosie.world.models import Points

# key poses -> a pose and a velocity per control step (linear, cubic)
type TrajectoryPlanner = Callable[[TrajectoryRequest], tuple[list[Pose], list[Velocity]]]


@dataclass(frozen=True, slots=True)
class TrajectoryPoint:
    """Where the robot should be at one control step, and how fast it should be moving."""

    pose: Pose
    velocity: Velocity


@dataclass(frozen=True, slots=True)
class TrajectoryRequest:
    key_poses: list[Pose]  # the path goes through them, in order
    speed: float  # m/s along the straight line from one key pose to the next
    sample_time: float  # s between control steps


@dataclass(frozen=True, slots=True)
class VisibilityGraph:
    """The corners of the free space, and which of them see each other."""

    free_space: (
        Polygon | MultiPolygon
    )  # the floor shrunk by the clearance, minus the grown obstacles
    vertices: Points  # n x 2
    neighbors: tuple[tuple[int, ...], ...]  # for each vertex, the vertices it sees
