import sys
import types

import pytest

from rosie.errors import HardwareUnavailableError
from rosie.motion.drivers.buses import open_i2c, open_serial


def fake_library(
    monkeypatch: pytest.MonkeyPatch, module: str, opener: str, error: bool
) -> list[tuple[object, ...]]:
    """Put a stand-in for the hardware library in sys.modules."""
    opened: list[tuple[object, ...]] = []

    def connect(*arguments: object) -> tuple[object, ...]:
        if error:
            raise OSError("no such device")
        opened.append(arguments)
        return arguments

    library = types.ModuleType(module)
    setattr(library, opener, connect)
    monkeypatch.setitem(sys.modules, module, library)
    return opened


def test_opens_a_serial_port(monkeypatch: pytest.MonkeyPatch) -> None:
    opened = fake_library(monkeypatch, "serial", "Serial", error=False)
    open_serial("/dev/ttyACM0", 9600)
    assert opened == [("/dev/ttyACM0", 9600)]


def test_opens_an_i2c_bus(monkeypatch: pytest.MonkeyPatch) -> None:
    opened = fake_library(monkeypatch, "smbus2", "SMBus", error=False)
    open_i2c(1)
    assert opened == [(1,)]


def test_missing_devices(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_library(monkeypatch, "serial", "Serial", error=True)
    fake_library(monkeypatch, "smbus2", "SMBus", error=True)
    with pytest.raises(HardwareUnavailableError, match="nothing answers on /dev/ttyACM0"):
        open_serial("/dev/ttyACM0", 9600)
    with pytest.raises(HardwareUnavailableError, match="no I2C bus 1"):
        open_i2c(1)


def test_missing_libraries(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "serial", None)
    monkeypatch.setitem(sys.modules, "smbus2", None)
    with pytest.raises(HardwareUnavailableError, match=r"pip install pyserial"):
        open_serial("/dev/ttyACM0", 9600)
    with pytest.raises(HardwareUnavailableError, match=r"pip install smbus2"):
        open_i2c(1)
