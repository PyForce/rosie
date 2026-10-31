from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from rosie.motion.models import Control, Wheels

if TYPE_CHECKING:
    from rosie.core import Robot


@dataclass(frozen=True, slots=True)
class Settings:
    profile: str  # one of rosie's robot profiles by name, or the folder of yours
    map: str  # the map the planner starts with
    interfaces: tuple[str, ...]  # what gives the robot its orders
    host: str  # where the web API listens
    port: int
    record: Path | None  # folder for a CSV of every planned movement


@dataclass(frozen=True, slots=True)
class Body:
    length: float  # m, front to back
    width: float  # m
    height: float  # m


@dataclass(frozen=True, slots=True)
class Profile:
    """A robot profile: its folder holds profile.toml, its pictures and its own maps."""

    id: str  # folder name
    directory: Path
    name: str
    trajectory: str  # linear or cubic
    video: str | None  # stream served by another program, ":port/path" on this host
    body: Body
    wheels: Wheels
    board: str  # virtual, arduino or md25
    board_settings: dict[str, Any]  # the rest of the [board] table, as the profile gives it
    control: Control
    sensors: dict[str, dict[str, Any]]  # sensor name -> its table, as the profile gives it

    @property
    def thumbnail(self) -> Path:
        return self.directory / "thumbnail.png"

    @property
    def vector(self) -> Path:
        return self.directory / "vector.svg"

    @property
    def maps(self) -> Path:
        return self.directory / "maps"


class SerialPort(Protocol):
    def write(self, data: bytes, /) -> int | None: ...

    def read(self, size: int = 1, /) -> bytes: ...


class I2CBus(Protocol):
    def write_byte(self, address: int, value: int, /) -> None: ...

    def read_byte(self, address: int, /) -> int: ...

    def write_byte_data(self, address: int, register: int, value: int, /) -> None: ...

    def write_i2c_block_data(self, address: int, register: int, data: list[int], /) -> None: ...

    def read_i2c_block_data(self, address: int, register: int, length: int, /) -> list[int]: ...


# an interface serves the robot while inside its context
type Interface = Callable[[Robot, Settings], AbstractAsyncContextManager[None]]
