import math

import pytest

from conftest import FakeClock
from rosie.motion.drivers.virtual import VirtualMotorDriver


def test_counts_what_the_wheels_turned(clock: FakeClock) -> None:
    driver = VirtualMotorDriver(1000, 8.0, clock)
    driver.set_speeds(math.pi, -math.pi)  # half a turn per second
    clock.now += 1
    driver.set_speeds(0, 2 * math.pi)
    clock.now += 0.5
    steps_1, steps_2, *_ = driver.read_delta_encoders_count_state()
    assert (steps_1, steps_2) == pytest.approx((500, 0))
    clock.now += 1
    assert driver.read_delta_encoders_count_state()[:2] == pytest.approx((0, 1000))


def test_clamps_to_the_maximum_speed(clock: FakeClock) -> None:
    driver = VirtualMotorDriver(1000, 2.0, clock)
    driver.set_speeds(5, -5)
    assert (driver.current_speed_1, driver.current_speed_2) == (2, -2)
