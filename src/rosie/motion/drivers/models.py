from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class VirtualBoard:
    """A simulated board: no settings."""


@dataclass(frozen=True, slots=True)
class ArduinoBoard:
    port: str = "/dev/ttyACM0"  # serial port
    baudrate: int = 9600


@dataclass(frozen=True, slots=True)
class MD25Board:
    bus: int = 1  # I2C bus number
    address: int = 0x58
    max_power: float = 127.0  # powers go from -max_power to max_power


class SerialPort(Protocol):
    def write(self, data: bytes, /) -> int | None: ...

    def read(self, size: int = 1, /) -> bytes: ...


class I2CBus(Protocol):
    def write_byte(self, address: int, value: int, /) -> None: ...

    def read_byte(self, address: int, /) -> int: ...

    def write_byte_data(self, address: int, register: int, value: int, /) -> None: ...

    def write_i2c_block_data(self, address: int, register: int, data: list[int], /) -> None: ...

    def read_i2c_block_data(self, address: int, register: int, length: int, /) -> list[int]: ...
