import logging
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import Any

from rosie.motion.controller import MovementController
from rosie.motion.drivers.arduino import ArduinoMotorDriver
from rosie.motion.drivers.md25 import MD25MotorDriver
from rosie.motion.drivers.virtual import VirtualMotorDriver
from rosie.motion.models import Pose, RobotParameters, TrajectoryParameters
from rosie.motion.motors import (
    HardwareSpeedMotorHandler,
    MotorHandler,
    PIDSpeedController,
    SoftwareSpeedMotorHandler,
)
from rosie.motion.odometry import RungeKutta2Localizer
from rosie.motion.recording import MovementRecorder
from rosie.motion.supervisors import SupervisorContainer
from rosie.motion.tracking import IOLinearizationTracker
from rosie.motion.trajectories import (
    CubicTrajectoryPlanner,
    LinearTrajectoryPlanner,
    TrajectoryPlanner,
)
from rosie.planning.planner import Planner
from rosie.profile import Profile

logger = logging.getLogger(__name__)

DEFAULT_MAP = "Gustavo's House"

ARDUINO_PORT = "/dev/ttyACM0"
ARDUINO_BAUDRATE = 9600

type Clock = Callable[[], float]
type MotorHandlerFactory = Callable[[Profile, RobotParameters, Clock], MotorHandler]


class Robot:
    """The robot core: everything rosie's interfaces can ask of the robot."""

    def __init__(
        self, profile: Profile, maps: dict[str, Path], recordings: Path | None, clock: Clock
    ) -> None:
        self.profile = profile
        self.parameters = robot_parameters(profile)
        self.supervisors = SupervisorContainer()
        # sensor name -> function reading it (plugins add theirs)
        self.sensors: dict[str, Callable[[], object]] = {}
        self.motion = movement_controller(profile, self.parameters, self.supervisors, clock)
        self.planner = Planner(maps)
        self.planner.use_map(DEFAULT_MAP)
        if recordings:
            self.supervisor().append(MovementRecorder(self.parameters, recordings))
        logger.info("profile: %s", profile.id)

    @property
    def sample_time(self) -> float:
        return self.motion.sample_time

    def tick(self) -> None:
        self.motion.tick()

    def stop(self) -> None:
        self.motion.movement_finish()

    def position(self) -> tuple[float, float, float]:
        pose = self.motion.odometry_localizer.pose
        return pose.x, pose.y, pose.theta

    def teleport(self, x: float, y: float, theta: float) -> None:
        self.motion.odometry_localizer.pose = Pose(x, y, theta)

    def go_to(self, x: float, y: float, t: float) -> None:
        """Drive to (x, y) in t seconds."""
        self._check_duration(t)
        self._track(
            TrajectoryParameters([Pose(*self.position()), Pose(x, y, 0.0)], t, self.sample_time)
        )

    def go_to_with_planner(self, x: float, y: float, t: float) -> None:
        """Drive to (x, y) around walls and furniture, t seconds per straight stretch."""
        self._check_duration(t)
        x0, y0, _ = self.position()
        clearance = 0.2 * max(self.profile.body.width, self.profile.body.length)
        _start, *corners = self.planner.route((x0, y0), (x, y), clearance)
        self.follow(corners, t)

    def follow(self, points: Sequence[Sequence[float]], t: float) -> None:
        """Drive through the points in order, t seconds from one to the next."""
        self._check_duration(t)
        poses = [Pose(*self.position()), *(Pose(p[0], p[1], 0.0) for p in points)]
        self._track(TrajectoryParameters(poses, t, self.sample_time))

    def start_open_loop_control(self) -> None:
        logger.debug("set mode: MANUAL")
        self.motion.movement_init(None)
        self.motion.movement_start()

    def add_movement(self, direction: list[float]) -> None:
        self.motion.direction = direction

    def stop_open_loop_control(self) -> None:
        logger.debug("set mode: AUTO")
        self.motion.movement_finish()

    def supervisor(self) -> SupervisorContainer:
        return self.supervisors

    def maps(self) -> Iterator[str]:
        return iter(self.planner.maps)

    def get_map(self, map_name: str) -> dict[str, Any] | None:
        return self.planner.get_map(map_name)

    def _check_duration(self, t: float) -> None:
        if t < self.sample_time:
            raise ValueError(f"the time must be at least one control step ({self.sample_time} s)")

    def _track(self, trajectory: TrajectoryParameters) -> None:
        self.motion.movement_init(trajectory)
        self.motion.movement_start()


def movement_controller(
    profile: Profile, parameters: RobotParameters, supervisors: SupervisorContainer, clock: Clock
) -> MovementController:
    planner = _choose(PLANNERS, "interpolation", profile.interpolation)()
    motors = _choose(MOTOR_HANDLERS, "board", profile.board)(profile, parameters, clock)
    return MovementController(
        supervisors,
        planner,
        RungeKutta2Localizer(parameters),
        IOLinearizationTracker(parameters),
        motors,
        parameters,
        clock,
    )


def robot_parameters(profile: Profile) -> RobotParameters:
    return RobotParameters(
        profile.wheels.radius,
        profile.wheels.distance,
        profile.wheels.encoder_steps,
        profile.tracking.b,
        profile.tracking.k1,
        profile.tracking.k2,
        profile.speed.ki,
        profile.speed.kd,
        profile.speed.kc,
        profile.speed.max_power,
        -profile.speed.max_power,
        profile.sample_time,
        profile.wheels.max_speed,
        profile.arrival_tolerance,
        profile.arrival_timeout,
    )


def _virtual_motors(_profile: Profile, parameters: RobotParameters, clock: Clock) -> MotorHandler:
    return HardwareSpeedMotorHandler(
        VirtualMotorDriver(parameters.steps_per_revolution, parameters.max_speed, clock)
    )


def _arduino_motors(profile: Profile, parameters: RobotParameters, _clock: Clock) -> MotorHandler:
    driver = ArduinoMotorDriver(profile.wheels.max_speed, ARDUINO_PORT, ARDUINO_BAUDRATE)
    driver.set_constants(parameters.constant_kc, parameters.constant_ki, parameters.constant_kd)
    return HardwareSpeedMotorHandler(driver)


def _md25_motors(_profile: Profile, parameters: RobotParameters, _clock: Clock) -> MotorHandler:
    speed_controller = PIDSpeedController(
        parameters.constant_kc,
        parameters.constant_ki,
        parameters.constant_kd,
        parameters.max_value_power,
        parameters.min_value_power,
    )
    return SoftwareSpeedMotorHandler(speed_controller, MD25MotorDriver(1, 0x58))


def _choose[T](options: dict[str, T], setting: str, value: str) -> T:
    if value not in options:
        raise ValueError(f"unsupported {setting}: {value} (known: {', '.join(options)})")
    return options[value]


PLANNERS: dict[str, Callable[[], TrajectoryPlanner]] = {
    "linear": LinearTrajectoryPlanner,
    "cubic": CubicTrajectoryPlanner,
}
MOTOR_HANDLERS: dict[str, MotorHandlerFactory] = {
    "virtual": _virtual_motors,
    "arduino": _arduino_motors,
    "md25": _md25_motors,
}
