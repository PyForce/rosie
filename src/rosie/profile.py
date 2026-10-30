"""
Robot profiles: a folder per robot with profile.toml, a picture
(thumbnail.png) and an icon (vector.svg). rosie looks in the user's
profiles folder first, then in its own.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

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
    tracking: Tracking
    speed: SpeedControl

    @property
    def thumbnail(self) -> Path:
        return self.directory / "thumbnail.png"

    @property
    def vector(self) -> Path:
        return self.directory / "vector.svg"


def load_profile(profile_id: str, search: list[Path]) -> Profile:
    """The profile `profile_id` from the first folder of `search` that has it."""
    for folder in search:
        path = folder / profile_id / "profile.toml"
        if path.is_file():
            return _parse(profile_id, path)
    raise ValueError(f"unknown profile {profile_id} (looked in {', '.join(map(str, search))})")


def _parse(profile_id: str, path: Path) -> Profile:
    data = tomllib.loads(path.read_text())
    try:
        control = data["control"]
        return Profile(
            id=profile_id,
            directory=path.parent,
            name=data["name"],
            board=data["board"],
            interpolation=data["interpolation"],
            video=data.get("video"),
            body=Body(**data["body"]),
            wheels=Wheels(**data["wheels"]),
            sample_time=control["sample_time"],
            tracking=Tracking(**control["tracking"]),
            speed=SpeedControl(**control["speed"]),
        )
    except (KeyError, TypeError) as error:
        raise ValueError(f"{path}: missing or unknown setting ({error})") from error
