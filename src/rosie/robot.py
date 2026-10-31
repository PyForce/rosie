"""
A robot built from its profile: its drive, trajectory and tracker, the
route planner with the robot's own maps and rosie's, and the sensors the
profile names.
"""

import logging
from functools import partial
from pathlib import Path

from rosie.control.models import MovementSupervisor
from rosie.control.tracking import io_linearization
from rosie.core import Robot
from rosie.errors import SetupError
from rosie.hardware.drive import open_drive
from rosie.hardware.sensors import open_sensors
from rosie.models import Clock, Profile
from rosie.planning.models import TrajectoryShape
from rosie.planning.path.maps import BUILTIN_MAPS, list_maps
from rosie.planning.path.planner import Planner
from rosie.planning.trajectory import cubic, linear
from rosie.recording import MovementRecorder

logger = logging.getLogger(__name__)


def build_robot(profile: Profile, map_name: str, recordings: Path | None, clock: Clock) -> Robot:
    sensors = open_sensors(profile)
    if profile.trajectory not in TRAJECTORIES:
        known = ", ".join(TRAJECTORIES)
        raise SetupError(f"unsupported trajectory: {profile.trajectory} (known: {known})")
    drive = open_drive(profile, clock)
    # the robot's own maps first: they win a name over rosie's
    planner = Planner(list_maps([profile.maps, BUILTIN_MAPS]))
    planner.use_map(map_name)
    supervisors: list[MovementSupervisor] = []
    if recordings:
        supervisors.append(MovementRecorder(profile.wheels, profile.control, recordings))
    logger.info("profile: %s", profile.id)
    return Robot(
        profile,
        drive,
        TRAJECTORIES[profile.trajectory],
        partial(io_linearization, profile.control.tracking, profile.wheels),
        planner,
        sensors,
        supervisors,
        clock,
    )


TRAJECTORIES: dict[str, TrajectoryShape] = {"linear": linear, "cubic": cubic}
