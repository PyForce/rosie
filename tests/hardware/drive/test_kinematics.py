import pytest

from rosie.hardware.drive.kinematics import compute_wheel_speeds
from rosie.models import Wheels

WHEELS = Wheels(radius=0.05, separation=0.3, encoder_resolution=360, max_speed=10.0)


@pytest.mark.parametrize(
    ("v", "omega", "speeds"),
    [
        (0.5, 0.0, (10.0, 10.0)),  # straight: both wheels at v / r
        (0.0, 1.0, (-3.0, 3.0)),  # on the spot, counter-clockwise: ω d/2 / r each way
        (0.5, 1.0, (7.0, 13.0)),
    ],
)
def test_compute_wheel_speeds(v: float, omega: float, speeds: tuple[float, float]) -> None:
    assert compute_wheel_speeds(v, omega, WHEELS) == pytest.approx(speeds)
