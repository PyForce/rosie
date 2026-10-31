from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

type Clock = Callable[[], float]  # s, only differences matter

type RecordedRow = tuple[float | None, ...]  # a recorded control step, one value per column


@dataclass(frozen=True, slots=True)
class Pose:
    x: float  # m
    y: float  # m
    theta: float  # rad, counter-clockwise from the x axis


@dataclass(frozen=True, slots=True)
class Velocity:
    x: float  # m/s
    y: float  # m/s
    theta: float  # rad/s


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
class TrackingGains:
    """Input-output linearization."""

    b: float  # m, the tracked point ahead of the wheel axis
    k1: float
    k2: float


@dataclass(frozen=True, slots=True)
class PIDGains:
    """The drive's wheel-speed PID: run by the Arduino shield, or by rosie for the MD25."""

    kc: float
    ki: float
    kd: float


@dataclass(frozen=True, slots=True)
class ControlSettings:
    sample_time: float  # s between control steps
    arrival_tolerance: float  # m: a planned movement ends this close to its last point
    arrival_timeout: float  # s it may take, after the planned time, to get that close
    tracking: TrackingGains


@dataclass(frozen=True, slots=True)
class Profile:
    """A robot profile: its folder holds profile.toml, its pictures and its own maps."""

    folder_name: str
    directory: Path
    name: str
    trajectory: str  # linear or cubic
    video: str | None  # stream served by another program, ":port/path" on this host
    body: Body
    wheels: Wheels
    drive_type: str  # virtual, arduino or md25
    drive_settings: dict[str, Any]  # the rest of the [drive] table, as the profile gives it
    drive_gains: PIDGains | None  # [drive.gains]; the virtual drive has no PID
    control: ControlSettings
    sensors: dict[str, dict[str, Any]]  # sensor name -> its table, as the profile gives it

    @property
    def picture(self) -> Path:
        return self.directory / "thumbnail.png"

    @property
    def icon(self) -> Path:
        return self.directory / "vector.svg"

    @property
    def maps_folder(self) -> Path:
        return self.directory / "maps"


@dataclass(frozen=True, slots=True)
class StartSettings:
    profile: str  # one of rosie's robot profiles by name, or the folder of yours
    map: str  # the map the planner starts with
    interfaces: tuple[str, ...]  # what gives the robot its orders
    host: str  # where the web API listens
    port: int
    record: Path | None  # folder for a CSV of every planned movement


ORIGIN = Pose(0.0, 0.0, 0.0)

STILL = Velocity(0.0, 0.0, 0.0)
