from collections.abc import Callable
from dataclasses import dataclass

type Clock = Callable[[], float]  # s, only differences matter


@dataclass(frozen=True, slots=True)
class Pose:
    x: float  # m
    y: float  # m
    theta: float  # rad, counter-clockwise from the x axis


@dataclass(frozen=True, slots=True)
class Velocity:
    x: float  # m/s
    y: float  # m/s
    theta: float  # rad/s


ORIGIN = Pose(0.0, 0.0, 0.0)
STILL = Velocity(0.0, 0.0, 0.0)

# encoder steps of wheel 1 and 2 since the previous reading, battery voltage (V),
# current of motor 1 and 2 (A)
type EncoderReading = tuple[float, float, float, float, float]


@dataclass(frozen=True, slots=True)
class TrajectoryParameters:
    key_poses: list[Pose]  # the path goes through them, in order
    segment_time: float  # s from one key pose to the next
    sample_time: float  # s between control steps


@dataclass(frozen=True, slots=True)
class Wheels:
    radius: float  # m
    distance: float  # m between the wheels
    encoder_steps: float  # per wheel turn
    max_speed: float  # rad/s


@dataclass(frozen=True, slots=True)
class Tracking:
    """Input-output linearization."""

    b: float  # m, the tracked point ahead of the wheel axis
    k1: float
    k2: float


@dataclass(frozen=True, slots=True)
class SpeedControl:
    """The wheel speed PID: on the board (arduino) or in rosie (md25)."""

    kc: float
    ki: float
    kd: float


@dataclass(frozen=True, slots=True)
class Control:
    sample_time: float  # s between control steps
    arrival_tolerance: float  # m: a planned movement ends this close to its last point
    arrival_timeout: float  # s it may take, after the planned time, to get that close
    tracking: Tracking
    speed: SpeedControl


# wheel 1 and 2 speed setpoints (rad/s), then the x and y speeds the tracker asked for
type TrackerOutput = tuple[float, float, float, float]


@dataclass(slots=True)
class PIDHistory:
    """One wheel's speed PID: what the incremental form needs from the previous steps."""

    error_1: float  # error one step ago
    error_2: float  # error two steps ago
    action_1: float  # control action one step ago


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


RESTING = RobotState(ORIGIN, ORIGIN, STILL, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


type Row = tuple[float | None, ...]  # a recorded control step, one value per column
