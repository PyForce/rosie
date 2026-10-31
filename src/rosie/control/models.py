from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from rosie.models import Pose, Velocity
from rosie.planning.models import Reference

# wheel 1 and 2 speeds to ask for (rad/s)
type SetPoints = tuple[float, float]
# wheel 1 and 2 speed setpoints (rad/s), then the x and y speeds the tracker asked for
type TrackerOutput = tuple[float, float, float, float]
# reference pose, reference velocity, the robot's pose -> TrackerOutput
type Tracker = Callable[[Pose, Velocity, Pose], TrackerOutput]


@dataclass(frozen=True, slots=True)
class RobotState:
    pose: Pose  # where the robot is on the map
    reference_pose: Pose | None  # None under manual control
    reference_velocity: Velocity | None
    tracker_x: float | None  # speeds asked by the trajectory tracker
    tracker_y: float | None
    wheel_1_speed: float  # rad/s
    wheel_1_setpoint: float
    wheel_1_current: float  # A
    wheel_2_speed: float
    wheel_2_setpoint: float
    wheel_2_current: float
    battery_voltage: float  # V
    elapsed_time: float  # s since the previous step


@dataclass(frozen=True, slots=True)
class Planned:
    """A planned movement: one reference per control step, and the next one to follow."""

    references: tuple[Reference, ...]
    next_index: int
    finished_at: float  # when the last reference was followed (clock time)

    @property
    def trajectory_done(self) -> bool:
        return self.next_index >= len(self.references)


@dataclass(frozen=True, slots=True)
class Manual:
    """Driving by hand: the commands of a keyboard or a joystick, each in [-1, 1]."""

    steering: float  # +1 right
    throttle: float  # +1 forward
    spin: float  # +1 clockwise, on the spot


type Movement = Planned | Manual


class MovementSupervisor(Protocol):
    """Follows each movement: its start, every control step, its end."""

    def movement_begin(self, expected_updates: int | None) -> None:
        """`expected_updates`: control steps of a planned movement, None under manual control."""

    def movement_update(self, robot_state: RobotState) -> None: ...

    def movement_end(self) -> None: ...
