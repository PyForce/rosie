"""
A robot built from its profile: the motion controller with the profile's
trajectory planner and motor board, the route planner with the robot's own
maps and rosie's, and the sensors the profile names.
"""

import logging
from functools import partial
from pathlib import Path

from rosie.boards import open_board
from rosie.core import Robot
from rosie.errors import SetupError
from rosie.models import Profile
from rosie.motion.controller import MotionController
from rosie.motion.models import Clock, TrajectoryShape
from rosie.motion.recording import MovementRecorder
from rosie.motion.supervisors import Supervisors
from rosie.motion.tracking import io_linearization
from rosie.motion.trajectories import cubic_trajectory, linear_trajectory
from rosie.planning.maps import BUILTIN_MAPS, list_maps
from rosie.planning.planner import Planner
from rosie.sensors import open_sensors

logger = logging.getLogger(__name__)


def build_robot(profile: Profile, map_name: str, recordings: Path | None, clock: Clock) -> Robot:
    supervisors = Supervisors()
    sensors = open_sensors(profile)
    motion = motion_controller(profile, supervisors, clock)
    # the robot's own maps first: they win a name over rosie's
    planner = Planner(list_maps([profile.maps, BUILTIN_MAPS]))
    planner.use_map(map_name)
    if recordings:
        supervisors.append(MovementRecorder(profile.wheels, profile.control, recordings))
    logger.info("profile: %s", profile.id)
    return Robot(profile, motion, planner, sensors, supervisors)


def motion_controller(profile: Profile, supervisors: Supervisors, clock: Clock) -> MotionController:
    if profile.trajectory not in TRAJECTORIES:
        known = ", ".join(TRAJECTORIES)
        raise SetupError(f"unsupported trajectory: {profile.trajectory} (known: {known})")
    return MotionController(
        supervisors,
        TRAJECTORIES[profile.trajectory],
        partial(io_linearization, profile.control.tracking, profile.wheels),
        open_board(profile, clock),
        profile.wheels,
        profile.control,
        clock,
    )


TRAJECTORIES: dict[str, TrajectoryShape] = {"linear": linear_trajectory, "cubic": cubic_trajectory}
