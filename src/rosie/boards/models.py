from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from rosie.models import Profile
from rosie.motion.models import Clock, EncoderReading


class Board(Protocol):
    """The motor board driving the robot's two wheels."""

    def read_encoders(self) -> EncoderReading | None:
        """Encoder steps of both wheels since the last reading, battery voltage, motor currents."""

    def set_speeds(
        self, speed_1: float, speed_2: float, measured_1: float, measured_2: float
    ) -> None:
        """Wheel speeds to reach (rad/s), and the ones just measured."""

    def stop(self) -> None: ...

    def reset(self) -> None:
        """Forget the previous movement, before a new one starts."""


# a board's type -> opening the board a profile describes
type BoardFactory = Callable[[Profile, Clock], Board]


@dataclass(frozen=True, slots=True)
class VirtualSettings:
    """A simulated board: no settings."""


@dataclass(frozen=True, slots=True)
class ArduinoSettings:
    port: str = "/dev/ttyACM0"  # serial port
    baudrate: int = 9600


@dataclass(frozen=True, slots=True)
class MD25Settings:
    bus: int = 1  # I2C bus number
    address: int = 0x58
    max_power: float = 127.0  # powers go from -max_power to max_power
