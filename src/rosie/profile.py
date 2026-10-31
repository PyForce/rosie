"""
Robot profiles: a folder per robot with profile.toml, a picture
(thumbnail.png), an icon (vector.svg) and, if you like, the robot's own
floor maps (maps/*.json). rosie's own robots are picked by name, yours by
the path of their folder.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROFILES_DIR = Path(__file__).parent / "profiles"


@dataclass(frozen=True, slots=True)
class Body:
    length: float  # m, front to back
    width: float  # m
    height: float  # m


@dataclass(frozen=True, slots=True)
class Wheels:
    radius: float  # m
    distance: float  # m between the wheels
    encoder_steps: float  # per wheel turn
    max_speed: float  # rad/s


@dataclass(frozen=True, slots=True)
class Tracking:
    b: float  # m, the tracked point ahead of the wheel axis
    k1: float
    k2: float


@dataclass(frozen=True, slots=True)
class SpeedControl:
    kc: float
    ki: float
    kd: float
    max_power: float  # md25: powers go from -max_power to max_power


@dataclass(frozen=True, slots=True)
class Profile:
    id: str  # folder name
    directory: Path
    name: str
    board: str  # virtual, arduino or md25
    interpolation: str  # linear or cubic
    video: str | None  # stream served by another program, ":port/path" on this host
    body: Body
    wheels: Wheels
    sample_time: float  # s between control steps
    arrival_tolerance: float  # m: a planned movement ends this close to its last point
    arrival_timeout: float  # s it may take, after the planned time, to get that close
    tracking: Tracking
    speed: SpeedControl
    sensors: dict[str, dict[str, Any]]  # sensor name -> its settings, as the profile gives them

    @property
    def thumbnail(self) -> Path:
        return self.directory / "thumbnail.png"

    @property
    def vector(self) -> Path:
        return self.directory / "vector.svg"

    @property
    def maps(self) -> Path:
        return self.directory / "maps"


def load_profile(robot: str) -> Profile:
    """One of rosie's robots by name (simubot), or yours by its folder (./my-robot)."""
    builtin = PROFILES_DIR / robot
    folder = builtin if "/" not in robot and builtin.is_dir() else Path(robot).expanduser()
    path = folder / "profile.toml"
    if not path.is_file():
        known = ", ".join(sorted(path.parent.name for path in PROFILES_DIR.glob("*/profile.toml")))
        raise ValueError(f"unknown robot {robot}: no {path} (rosie's own: {known})")
    return _parse(path)


def _parse(path: Path) -> Profile:
    data = tomllib.loads(path.read_text())
    try:
        control = data["control"]
        return Profile(
            id=path.parent.resolve().name,
            directory=path.parent,
            name=data["name"],
            board=data["board"],
            interpolation=data["interpolation"],
            video=data.get("video"),
            body=Body(**data["body"]),
            wheels=Wheels(**data["wheels"]),
            sample_time=control["sample_time"],
            arrival_tolerance=control["arrival_tolerance"],
            arrival_timeout=control["arrival_timeout"],
            tracking=Tracking(**control["tracking"]),
            speed=SpeedControl(**control["speed"]),
            sensors=data.get("sensors", {}),
        )
    except (KeyError, TypeError) as error:
        raise ValueError(f"{path}: missing or unknown setting ({error})") from error
