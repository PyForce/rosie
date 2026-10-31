import struct

import pytest

from conftest import FakeSerial
from rosie.hardware.drive.devices.arduino import ArduinoDrive


class BrokenSerial(FakeSerial):
    def write(self, data: bytes, /) -> int:
        raise OSError("unplugged")


@pytest.fixture
def serial() -> FakeSerial:
    return FakeSerial()


@pytest.fixture
def driver(serial: FakeSerial) -> ArduinoDrive:
    return ArduinoDrive(serial)


def state(pulses_1: int, pulses_2: int, battery: int) -> bytes:
    return b"\xa9" + struct.pack("i", pulses_1) + struct.pack("i", pulses_2) + bytes([battery])


def test_speeds_go_to_the_board_wheel_2_first(driver: ArduinoDrive, serial: FakeSerial) -> None:
    driver.set_speeds(1.5, -2.0, 0, 0)
    assert serial.written == [struct.pack("<Bff", 0xA7, -2.0, 1.5)]


def test_pid_constants_and_encoder_reset(driver: ArduinoDrive, serial: FakeSerial) -> None:
    driver.set_constants(1.0, 0.5, 0.25)
    driver.reset_encoders()
    assert serial.written == [struct.pack("<Bfff", 0xA6, 1.0, 0.5, 0.25), b"\xaa"]


def test_reads_encoder_deltas_with_the_wheels_swapped(
    driver: ArduinoDrive, serial: FakeSerial
) -> None:
    serial.incoming += state(100, 40, 90)
    assert driver.read() == (40, 100, 90, 0, 0)
    serial.incoming += state(130, 30, 89)
    assert driver.read() == (-10, 30, 89, 0, 0)
    assert serial.written == [b"\xa8", b"\xa8"]


def test_ignores_an_unexpected_answer(driver: ArduinoDrive, serial: FakeSerial) -> None:
    serial.incoming += b"\x00"
    assert driver.read() is None


def test_a_cut_answer_reads_as_still(driver: ArduinoDrive, serial: FakeSerial) -> None:
    serial.incoming += b"\xa9\x01\x02"
    assert driver.read() == (0, 0, 0, 0, 0)


def test_write_errors_are_logged_not_raised(caplog: pytest.LogCaptureFixture) -> None:
    driver = ArduinoDrive(BrokenSerial())
    driver.set_speeds(1, 1, 0, 0)
    driver.set_constants(1, 1, 1)
    driver.reset_encoders()
    assert driver.read() == (0, 0, 0, 0, 0)
    assert [record.message for record in caplog.records] == [
        "setting speeds",
        "setting constants",
        "resetting encoders",
        "reading encoders",
    ]
