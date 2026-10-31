from collections.abc import Callable
from dataclasses import dataclass

from rosie.models import Pose, Velocity

# key poses -> a pose and a velocity per control step (linear, cubic)
type TrajectoryShape = Callable[[TrajectoryParameters], tuple[list[Pose], list[Velocity]]]


@dataclass(frozen=True, slots=True)
class Reference:
    """Where the robot should be at one control step, and how fast it should be moving."""

    pose: Pose
    velocity: Velocity


@dataclass(frozen=True, slots=True)
class TrajectoryParameters:
    key_poses: list[Pose]  # the path goes through them, in order
    segment_time: float  # s from one key pose to the next
    sample_time: float  # s between control steps
