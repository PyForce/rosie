"""
A robot built from its profile: the motion controller with the profile's
trajectory planner and motor board, the route planner with the robot's own
maps and rosie's, and the sensors the profile names.
"""

import logging
from pathlib import Path

from rosie.core import Robot
from rosie.models import MotorHandlerFactory, Profile, SensorFactory
from rosie.motion.controller import MotionController
from rosie.motion.drivers.arduino import ArduinoMotorDriver
from rosie.motion.drivers.buses import open_i2c, open_serial
from rosie.motion.drivers.md25 import MD25MotorDriver
from rosie.motion.drivers.models import ArduinoBoard, MD25Board, VirtualBoard
from rosie.motion.drivers.virtual import VirtualMotorDriver
from rosie.motion.models import Clock
from rosie.motion.motors import (
    HardwareSpeedMotorHandler,
    MotorHandler,
    PIDSpeedController,
    SoftwareSpeedMotorHandler,
)
from rosie.motion.odometry import RungeKutta2Localizer
from rosie.motion.recording import MovementRecorder
from rosie.motion.supervisors import Supervisors
from rosie.motion.tracking import IOLinearizationTracker
from rosie.motion.trajectories import (
    CubicTrajectoryPlanner,
    LinearTrajectoryPlanner,
    TrajectoryPlanner,
)
from rosie.planning.maps import MAPS_DIR, list_maps
from rosie.planning.planner import Planner
from rosie.sensors import usound

logger = logging.getLogger(__name__)


def build_robot(profile: Profile, map_name: str, recordings: Path | None, clock: Clock) -> Robot:
    supervisors = Supervisors()
    sensors = {
        name: _choose(SENSORS, "sensor", name)(table) for name, table in profile.sensors.items()
    }
    motion = motion_controller(profile, supervisors, clock)
    # the robot's own maps first: they win a name over rosie's
    planner = Planner(list_maps([profile.maps, MAPS_DIR]))
    planner.use_map(map_name)
    if recordings:
        supervisors.append(MovementRecorder(profile.wheels, profile.control, recordings))
    logger.info("profile: %s", profile.id)
    return Robot(profile, motion, planner, sensors, supervisors)


def motion_controller(profile: Profile, supervisors: Supervisors, clock: Clock) -> MotionController:
    return MotionController(
        supervisors,
        _choose(TRAJECTORIES, "trajectory", profile.trajectory)(),
        RungeKutta2Localizer(profile.wheels),
        IOLinearizationTracker(profile.control.tracking, profile.wheels),
        _choose(BOARDS, "board", profile.board)(profile, clock),
        profile.wheels,
        profile.control,
        clock,
    )


def _virtual_motors(profile: Profile, clock: Clock) -> MotorHandler:
    _board_settings(VirtualBoard, profile)
    wheels = profile.wheels
    return HardwareSpeedMotorHandler(
        VirtualMotorDriver(wheels.encoder_steps, wheels.max_speed, clock)
    )


def _arduino_motors(profile: Profile, _clock: Clock) -> MotorHandler:
    board = _board_settings(ArduinoBoard, profile)
    driver = ArduinoMotorDriver(open_serial(board.port, board.baudrate), profile.wheels.max_speed)
    speed = profile.control.speed
    driver.set_constants(speed.kc, speed.ki, speed.kd)
    return HardwareSpeedMotorHandler(driver)


def _md25_motors(profile: Profile, _clock: Clock) -> MotorHandler:
    board = _board_settings(MD25Board, profile)
    return SoftwareSpeedMotorHandler(
        PIDSpeedController(profile.control.speed, board.max_power),
        MD25MotorDriver(open_i2c(board.bus), board.address),
    )


def _board_settings[T](board: type[T], profile: Profile) -> T:
    try:
        return board(**profile.board_settings)
    except TypeError as error:
        raise ValueError(f"[board] of {profile.id}: unknown setting ({error})") from error


def _choose[T](options: dict[str, T], setting: str, value: str) -> T:
    if value not in options:
        raise ValueError(f"unsupported {setting}: {value} (known: {', '.join(options)})")
    return options[value]


TRAJECTORIES: dict[str, type[TrajectoryPlanner]] = {
    "linear": LinearTrajectoryPlanner,
    "cubic": CubicTrajectoryPlanner,
}
BOARDS: dict[str, MotorHandlerFactory] = {
    "virtual": _virtual_motors,
    "arduino": _arduino_motors,
    "md25": _md25_motors,
}
SENSORS: dict[str, SensorFactory] = {"usound": usound.open_sensor}
