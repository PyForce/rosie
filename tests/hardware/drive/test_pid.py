import pytest

from rosie.hardware.drive.pid import RESTING_PID, regulate_speed
from rosie.models import PIDGains


@pytest.mark.parametrize(
    ("ki", "kd", "actions"),
    [
        pytest.param(0, 0, [20, 10, 5], id="proportional"),
        # incremental forms: kc e + (ki - kc) e[-1] + u[-1], and with kd the full PID
        pytest.param(0.5, 0, [20, 11, 6.5], id="proportional-integral"),
        pytest.param(0.5, 0.1, [21.2, 11.4, 6.7], id="with derivative"),
    ],
)
def test_regulate_speed(ki: float, kd: float, actions: list[float]) -> None:
    gains = PIDGains(kc=10, ki=ki, kd=kd)
    history = RESTING_PID
    powers = []
    for error in [2, 1, 0.5]:
        power, history = regulate_speed(gains, 100, history, error)
        powers.append(power)
    assert powers == pytest.approx(actions)


def test_regulate_speed_saturates() -> None:
    gains = PIDGains(kc=10, ki=0.5, kd=0)
    assert regulate_speed(gains, 30, RESTING_PID, 10)[0] == 30
    assert regulate_speed(gains, 30, RESTING_PID, -10)[0] == -30
