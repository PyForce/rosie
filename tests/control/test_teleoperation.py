import math

import pytest

from rosie.control.teleoperation import from_keys

MAX_SPEED = 10.0


@pytest.mark.parametrize(
    ("keys", "expected"),
    [((0, 1, 0), (8, 8)), ((0, 0, 1), (8, -8)), ((1, 0, 0), (0, 0)), ((0, 0, 0), (0, 0))],
)
def test_from_keys(keys: tuple[float, float, float], expected: tuple[float, float]) -> None:
    assert from_keys(keys, MAX_SPEED) == pytest.approx(expected)


def test_steering_slows_one_wheel() -> None:
    wheel_1, wheel_2 = from_keys((1, 1, 0), MAX_SPEED)
    assert wheel_1 == 8
    assert wheel_2 == pytest.approx(8 * (1 - 8 / 10))  # steer by 8 rad/s of a 10 rad/s wheel
    assert not math.isclose(wheel_1, wheel_2)
