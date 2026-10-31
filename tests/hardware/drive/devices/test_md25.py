import pytest

from conftest import FakeI2C
from rosie.hardware.drive.devices.md25 import MD25Drive
from rosie.models import PIDGains

ADDRESS = 0x58


def block(
    encoder_1: int, encoder_2: int, volts: int = 120, current_1: int = 5, current_2: int = 7
) -> list[int]:
    return [
        *(encoder_1 % 2**32).to_bytes(4),
        *(encoder_2 % 2**32).to_bytes(4),
        volts,
        current_1,
        current_2,
    ]


@pytest.fixture
def bus() -> FakeI2C:
    return FakeI2C()


@pytest.fixture
def driver(bus: FakeI2C) -> MD25Drive:
    driver = MD25Drive(bus, ADDRESS, PIDGains(kc=10, ki=0, kd=0), 100)
    bus.calls.clear()
    return driver


def test_sets_the_board_up(bus: FakeI2C) -> None:
    MD25Drive(bus, ADDRESS, PIDGains(kc=10, ki=0, kd=0), 100)
    assert bus.calls == [
        ("write_byte_data", ADDRESS, 16, 32),  # reset the encoders
        ("write_byte_data", ADDRESS, 15, 1),  # mode 1: signed speeds
        ("write_byte_data", ADDRESS, 16, 48),  # no automatic speed regulation
        ("write_byte_data", ADDRESS, 14, 10),  # acceleration
    ]


def test_powers(driver: MD25Drive, bus: FakeI2C) -> None:
    driver.set_powers(20.7, -15.2)
    assert bus.calls == [("write_block", ADDRESS, 0, [20, -15])]


def test_reads_deltas_battery_and_currents(driver: MD25Drive, bus: FakeI2C) -> None:
    bus.blocks += [block(50, -30), block(120, -100)]
    assert driver.read() == (50, -30, 12.0, 0.5, 0.7)
    assert driver.read() == (70, -70, 12.0, 0.5, 0.7)


def test_a_jump_is_a_glitch(driver: MD25Drive, bus: FakeI2C) -> None:
    bus.blocks += [block(50, 50), block(5000, 100), block(40, 2000)]
    driver.read()
    bus.calls.clear()
    assert driver.read()[:2] == (50, 50)  # wheel 1 jumped
    assert ("write_byte_data", ADDRESS, 16, 32) in bus.calls
    # counting starts again from 0
    assert driver.read()[:2] == (40, 50)  # wheel 2 jumped


def test_resets_before_overflowing(driver: MD25Drive, bus: FakeI2C) -> None:
    driver.prev_encoder_count_1 = 2_000_000_000
    bus.blocks += [block(2_000_000_100, 0)]
    assert driver.read()[:2] == (100, 0)
    assert driver.prev_encoder_count_1 == 0
    assert bus.calls[-1] == ("write_byte_data", ADDRESS, 16, 32)


def test_reset(driver: MD25Drive, bus: FakeI2C) -> None:
    bus.blocks += [block(50, 50)]
    driver.read()
    driver.reset()
    assert (driver.prev_encoder_count_1, driver.prev_delta_encoder_count_2) == (0, 0)
    assert bus.calls[-1] == ("write_byte_data", ADDRESS, 16, 32)


def test_rosie_controls_the_speeds(driver: MD25Drive, bus: FakeI2C) -> None:
    driver.set_speeds(3.0, 2.0, 1.0, 0.0)  # proportional: 10 x the speed error
    assert bus.calls[-1] == ("write_block", ADDRESS, 0, [20, 20])
    driver.stop()
    assert bus.calls[-1] == ("write_block", ADDRESS, 0, [0, 0])
