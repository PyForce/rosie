"""
The hardware connections the boards talk through. Their libraries are only
needed by robots with such a board, so they're imported when a bus is opened.
"""

import importlib
from types import ModuleType

from rosie.errors import HardwareUnavailableError
from rosie.models import I2CBus, SerialPort


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
