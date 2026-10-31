import pytest

from rosie.hardware.drive.pid import RESTING_PID, regulate_speed
from rosie.models import PIDGains


@pytest.mark.parametrize(
    ("ki", "kd", "powers"),
    [
        pytest.param(0, 0, [20, 10, 5], id="proportional"),
        # one formula for all: the power changes by kc (e - e₋₁) + ki e + kd (e - 2 e₋₁ + e₋₂)
        pytest.param(0.5, 0, [21, 11.5, 6.75], id="proportional-integral"),
        pytest.param(0.5, 0.1, [21.2, 11.4, 6.7], id="with derivative"),
    ],
)
def test_regulate_speed(ki: float, kd: float, powers: list[float]) -> None:
    gains = PIDGains(kc=10, ki=ki, kd=kd)
    state = RESTING_PID
    steps = []
    for error in [2, 1, 0.5]:
        power, state = regulate_speed(gains, 100, state, error)
        steps.append(power)
    assert steps == pytest.approx(powers)


def test_regulate_speed_saturates() -> None:
    gains = PIDGains(kc=10, ki=0.5, kd=0)
    assert regulate_speed(gains, 30, RESTING_PID, 10)[0] == 30
    assert regulate_speed(gains, 30, RESTING_PID, -10)[0] == -30
