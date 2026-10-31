"""
A robot built from its profile: its drive, trajectory planner and tracker, the
route planner with the robot's own maps and rosie's, and the sensors the
profile names.
"""

import logging
from functools import partial
from pathlib import Path

from rosie.control.models import MovementObserver
from rosie.control.tracking import track_by_io_linearization
from rosie.core import Robot
from rosie.errors import SetupError
from rosie.hardware.drive import open_drive
from rosie.hardware.sensors import open_sensors
from rosie.models import Clock, Profile
from rosie.planning.models import TrajectoryPlanner
from rosie.planning.path.maps import BUILTIN_MAPS, list_maps
from rosie.planning.path.planner import Planner
from rosie.planning.trajectory import plan_cubic, plan_linear
from rosie.recording import MovementRecorder

logger = logging.getLogger(__name__)


def build_robot(profile: Profile, map_name: str, recordings: Path | None, clock: Clock) -> Robot:
    sensors = open_sensors(profile)
    if profile.trajectory_planner not in TRAJECTORY_PLANNERS:
        known = ", ".join(TRAJECTORY_PLANNERS)
        raise SetupError(
            f"unsupported trajectory planner: {profile.trajectory_planner} (known: {known})"
        )
    drive = open_drive(profile, clock)
    # the robot's own maps first: they win a name over rosie's
    planner = Planner(list_maps([profile.maps_folder, BUILTIN_MAPS]))
    planner.use_map(map_name)
    observers: list[MovementObserver] = []
    if recordings:
        observers.append(
            MovementRecorder(profile.wheels, profile.control, profile.drive_gains, recordings)
        )
    logger.info("profile: %s", profile.folder_name)
    return Robot(
        profile,
        drive,
        TRAJECTORY_PLANNERS[profile.trajectory_planner],
        partial(track_by_io_linearization, profile.control.tracking, profile.wheels),
        planner,
        sensors,
        observers,
        clock,
    )


TRAJECTORY_PLANNERS: dict[str, TrajectoryPlanner] = {"linear": plan_linear, "cubic": plan_cubic}
