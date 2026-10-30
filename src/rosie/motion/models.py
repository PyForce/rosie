from dataclasses import dataclass


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
    constant_k: float  # cubic planner: weight of the key poses' headings


@dataclass(frozen=True, slots=True)
class RobotParameters:
    wheel_radius: float  # m
    wheel_distance: float  # m
    steps_per_revolution: float  # encoder steps per wheel turn
    constant_b: float  # trajectory tracking
    constant_k1: float
    constant_k2: float
    constant_ki: float  # speed PID
    constant_kd: float
    constant_kc: float
    max_value_power: float
    min_value_power: float
    sample_time: float  # s between control steps
    max_speed: float  # rad/s of a wheel


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
