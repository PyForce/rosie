from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from shapely.geometry import Polygon

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
    segment_time: float  # s from one key pose to the next
    sample_time: float  # s between control steps


@dataclass(frozen=True, slots=True)
class VisibilityGraph:
    vertices: Points
    adjacency: np.ndarray  # n x n, non-zero where two vertices see each other
    free_space: Polygon
    obstacles: list[Polygon]
