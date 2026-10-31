import math

import pytest

from conftest import FakeClock
from rosie.hardware.drive.devices.virtual import VirtualDrive


def test_counts_what_the_wheels_turned(clock: FakeClock) -> None:
    driver = VirtualDrive(1000, 8.0, clock)
    driver.set_speeds(math.pi, -math.pi, 0, 0)  # half a turn per second
    clock.now += 1
    driver.set_speeds(0, 2 * math.pi, 0, 0)
    clock.now += 0.5
    reading = driver.read()
    steps_1, steps_2 = reading.steps_1, reading.steps_2
    assert (steps_1, steps_2) == pytest.approx((500, 0))
    clock.now += 1
    reading = driver.read()
    assert (reading.steps_1, reading.steps_2) == pytest.approx((0, 1000))


def test_clamps_to_the_maximum_speed(clock: FakeClock) -> None:
    driver = VirtualDrive(1000, 2.0, clock)
    driver.set_speeds(5, -5, 0, 0)
    assert (driver.current_speed_1, driver.current_speed_2) == (2, -2)
