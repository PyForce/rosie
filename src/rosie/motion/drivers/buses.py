"""
The hardware connections the boards talk through. Their libraries are only
needed by robots with such a board, so they're imported when a bus is opened.
"""

import importlib
from types import ModuleType
from typing import Protocol

from rosie.errors import HardwareUnavailableError


class SerialPort(Protocol):
    def write(self, data: bytes, /) -> int | None: ...

    def read(self, size: int = 1, /) -> bytes: ...


class I2CBus(Protocol):
    def write_byte(self, address: int, value: int, /) -> None: ...

    def read_byte(self, address: int, /) -> int: ...

    def write_byte_data(self, address: int, register: int, value: int, /) -> None: ...

    def write_i2c_block_data(self, address: int, register: int, data: list[int], /) -> None: ...

    def read_i2c_block_data(self, address: int, register: int, length: int, /) -> list[int]: ...


def open_serial(port: str, baudrate: int) -> SerialPort:
    serial = _library("serial", "pyserial")
    try:
        connection: SerialPort = serial.Serial(port, baudrate)
    except OSError as error:
        raise HardwareUnavailableError(f"nothing answers on {port}") from error
    return connection


def open_i2c(number: int) -> I2CBus:
    smbus2 = _library("smbus2", "smbus2")
    try:
        bus: I2CBus = smbus2.SMBus(number)
    except OSError as error:
        raise HardwareUnavailableError(f"no I2C bus {number}") from error
    return bus


def _library(module: str, package: str) -> ModuleType:
    try:
        return importlib.import_module(module)
    except ModuleNotFoundError as error:
        raise HardwareUnavailableError(
            f"this board needs {package} (pip install {package})"
        ) from error
