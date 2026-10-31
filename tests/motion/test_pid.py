import pytest

from rosie.motion.models import SpeedControl
from rosie.motion.pid import PIDSpeedController


@pytest.mark.parametrize(
    ("ki", "kd", "actions"),
    [
        pytest.param(0, 0, [20, 10, 5], id="proportional"),
        # incremental forms: kc e + (ki - kc) e[-1] + u[-1], and with kd the full PID
        pytest.param(0.5, 0, [20, 11, 6.5], id="proportional-integral"),
        pytest.param(0.5, 0.1, [21.2, 11.4, 6.7], id="with derivative"),
    ],
)
def test_pid(ki: float, kd: float, actions: list[float]) -> None:
    pid = PIDSpeedController(SpeedControl(kc=10, ki=ki, kd=kd), 100)
    errors = [2, 1, 0.5]
    assert [pid.regulate(error, 0, 0, 0)[0] for error in errors] == pytest.approx(actions)


def test_pid_saturates_and_resets() -> None:
    pid = PIDSpeedController(SpeedControl(kc=10, ki=0.5, kd=0), 30)
    assert pid.regulate(10, -10, 0, 0) == (30, -30)
    pid.reset()
    assert pid.regulate(1, 0, 0, 0) == (10, 0)
