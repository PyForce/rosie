"""
Robot profiles: a folder per robot with profile.toml, a picture
(thumbnail.png), an icon (vector.svg) and, if you like, the robot's own
floor maps (maps/*.json). rosie's own profiles are picked by name, yours by
the path of their folder.
"""

import tomllib
from pathlib import Path
from typing import Any

from rosie.errors import SetupError
from rosie.models import Body, Control, PIDGains, Profile, Tracking, Wheels

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
        gains = drive.pop("gains", None)
        control = data["control"]
        return Profile(
            id=path.parent.resolve().name,
            directory=path.parent,
            name=data["name"],
            trajectory=data["trajectory"],
            video=data.get("video"),
            body=Body(**data["body"]),
            wheels=Wheels(**data["wheels"]),
            drive=drive.pop("type"),
            drive_settings=drive,
            gains=None if gains is None else PIDGains(**gains),
            control=Control(
                sample_time=control["sample_time"],
                arrival_tolerance=control["arrival_tolerance"],
                arrival_timeout=control["arrival_timeout"],
                tracking=Tracking(**control["tracking"]),
            ),
            sensors=data.get("sensors", {}),
        )
    except (KeyError, TypeError) as error:
        raise SetupError(f"{path}: missing or unknown setting ({error})") from error


def read_table[T](settings: type[T], table: dict[str, Any], where: str) -> T:
    """A table of the profile as its settings dataclass; `where` names the table in the error."""
    try:
        return settings(**table)
    except TypeError as error:
        raise SetupError(f"{where}: unknown setting ({error})") from error
