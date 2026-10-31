"""
Robot profiles: a folder per robot with profile.toml, a picture
(thumbnail.png), an icon (vector.svg) and, if you like, the robot's own
floor maps (maps/*.geojson). rosie's own profiles are picked by name, yours by
the path of their folder.
"""

import tomllib
from pathlib import Path
from typing import Any

from rosie.errors import SetupError
from rosie.models import (
    Body,
    CameraSettings,
    ControlSettings,
    PIDGains,
    PlanningSettings,
    Profile,
    RegulationGains,
    RegulationSettings,
    TeleoperationSettings,
    TrackingGains,
    TrackingSettings,
    Wheels,
)

BUILTIN_PROFILES = Path(__file__).parent / "builtin" / "profiles"


def load_profile(profile: str) -> Profile:
    """One of rosie's profiles by name (simubot), or yours by its folder (./my-robot)."""
    builtin = BUILTIN_PROFILES / profile
    folder = builtin if "/" not in profile and builtin.is_dir() else Path(profile).expanduser()
    path = folder / "profile.toml"
    if not path.is_file():
        known = ", ".join(
            sorted(path.parent.name for path in BUILTIN_PROFILES.glob("*/profile.toml"))
        )
        raise SetupError(f"unknown robot profile {profile}: no {path} (rosie's own: {known})")
    return _parse(path)


def _parse(path: Path) -> Profile:
    data = tomllib.loads(path.read_text())
    if not isinstance(data.get("drive"), dict):
        raise SetupError(
            f'{path}: needs a [drive] table, with its type = "virtual", "arduino" or "md25"'
        )
    try:
        drive: dict[str, Any] = dict(data["drive"])
        drive_gains = drive.pop("gains", None)
        camera = data.get("camera")
        control = data["control"]
        tracking = control["tracking"]
        regulation = control["regulation"]
        return Profile(
            folder_name=path.parent.resolve().name,
            directory=path.parent,
            name=data["name"],
            body=Body(**data["body"]),
            wheels=Wheels(**data["wheels"]),
            drive_type=drive.pop("type"),
            drive_settings=drive,
            drive_gains=None if drive_gains is None else PIDGains(**drive_gains),
            camera=None if camera is None else CameraSettings(**camera),
            sensors=data.get("sensors", {}),
            planning=PlanningSettings(**data["planning"]),
            control=ControlSettings(
                sample_time=control["sample_time"],
                tracking=TrackingSettings(
                    lookahead=tracking["lookahead"], gains=TrackingGains(**tracking["gains"])
                ),
                regulation=RegulationSettings(
                    tolerance=regulation["tolerance"],
                    timeout=regulation["timeout"],
                    gains=RegulationGains(**regulation.get("gains", {})),
                ),
                teleoperation=TeleoperationSettings(**control.get("teleoperation", {})),
            ),
        )
    except (KeyError, TypeError) as error:
        raise SetupError(f"{path}: missing or unknown setting ({error})") from error


def read_table[T](settings: type[T], table: dict[str, Any], where: str) -> T:
    """A table of the profile as its settings dataclass; `where` names the table in the error."""
    try:
        return settings(**table)
    except TypeError as error:
        raise SetupError(f"{where}: unknown setting ({error})") from error
