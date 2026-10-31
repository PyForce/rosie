import pytest

from rosie.control.teleoperation import steer

MAX_SPEED = 10.0  # rad/s


@pytest.mark.parametrize(
    ("steering", "throttle", "spin", "wheels"),
    [
        (0, 1, 0, (8, 8)),  # full throttle: both wheels at MANUAL_SPEED
        (0, 0, 1, (8, -8)),  # spin clockwise, on the spot
        (1, 0, 0, (0, 0)),  # steering alone does nothing
        (0, 0, 0, (0, 0)),
    ],
)
def test_steer(steering: float, throttle: float, spin: float, wheels: tuple[float, float]) -> None:
    assert steer(steering, throttle, spin, MAX_SPEED) == pytest.approx(wheels)


@pytest.mark.parametrize(("steering", "slowed"), [(1, 1), (-1, 0)])
def test_steering_slows_the_wheel_on_its_side(steering: float, slowed: int) -> None:
    wheels = steer(steering, 1, 0, MAX_SPEED)
    assert wheels[slowed] == pytest.approx(8 * (1 - 8 / 10))  # steer by 8 rad/s of a 10 rad/s wheel
    assert wheels[1 - slowed] == 8
