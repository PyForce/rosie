from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from rosie.models import Clock, Profile

# a drive's type -> opening the drive a profile describes
type DriveFactory = Callable[[Profile, Clock], Drive]


@dataclass(frozen=True, slots=True)
class DriveReading:
    """What a drive measured since its previous reading."""

    steps_1: float  # encoder steps of wheel 1
    steps_2: float
    battery_voltage: float  # V
    current_1: float  # A, motor 1
    current_2: float


@dataclass(frozen=True, slots=True)
class VirtualDriveSettings:
    """A simulated drive: no settings."""


@dataclass(frozen=True, slots=True)
class ArduinoDriveSettings:
    port: str = "/dev/ttyACM0"  # serial port
    baudrate: int = 9600


@dataclass(frozen=True, slots=True)
class MD25DriveSettings:
    bus: int = 1  # I2C bus number
    address: int = 0x58
    max_power: float = 127.0  # powers go from -max_power to max_power


@dataclass(frozen=True, slots=True)
class PIDState:
    """One wheel's speed PID: what the incremental form needs from the previous steps."""

    error_1: float  # error one step ago
    error_2: float  # error two steps ago
    power: float  # power one step ago


class Drive(Protocol):
    """The drive: the motors turning the two wheels at the speeds asked, and their encoders."""

    def read(self) -> DriveReading | None:
        """Encoder steps of both wheels since the last reading, battery voltage, motor currents."""

    def set_speeds(
        self, speed_1: float, speed_2: float, measured_1: float, measured_2: float
    ) -> None:
        """Wheel speeds to reach (rad/s), and the ones just measured."""

    def stop(self) -> None: ...

    def reset(self) -> None:
        """Forget the previous movement, before a new one starts."""
