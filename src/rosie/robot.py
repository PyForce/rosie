"""
A robot built from its profile: its drive, trajectory planner and tracker, the
maps (the robot's own and rosie's) and the world it starts in, and the sensors the
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
from rosie.planning.trajectory import TRAJECTORY_PLANNERS
from rosie.recording import MovementRecorder
from rosie.world.maps import BUILTIN_MAPS, list_maps, load_world

logger = logging.getLogger(__name__)


def build_robot(profile: Profile, map_name: str, recordings: Path | None, clock: Clock) -> Robot:
    sensors = open_sensors(profile)
    if profile.planning.planner not in TRAJECTORY_PLANNERS:
        known = ", ".join(TRAJECTORY_PLANNERS)
        raise SetupError(f"unknown trajectory planner: {profile.planning.planner} (known: {known})")
    drive = open_drive(profile, clock)
    # the robot's own maps first: they win a name over rosie's
    map_files = list_maps([profile.maps_folder, BUILTIN_MAPS])
    if map_name not in map_files:
        raise SetupError(f"unknown map: {map_name}")
    observers: list[MovementObserver] = []
    if recordings:
        observers.append(
            MovementRecorder(profile.wheels, profile.control, profile.drive_gains, recordings)
        )
    logger.info("profile: %s", profile.folder_name)
    return Robot(
        profile,
        drive,
        profile.planning.planner,
        partial(track_by_io_linearization, profile.control.tracking, profile.wheels),
        map_files,
        load_world(map_files[map_name]),
        sensors,
        observers,
        clock,
    )
