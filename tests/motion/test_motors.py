import pytest

from conftest import FakeI2C
from rosie.motion.drivers.md25 import MD25MotorDriver
from rosie.motion.models import SpeedControl
from rosie.motion.motors import PIDSpeedController, SoftwareSpeedMotorHandler


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


def test_software_speed_control_on_a_power_board() -> None:
    bus = FakeI2C()
    driver = MD25MotorDriver(bus, 0x58)
    handler = SoftwareSpeedMotorHandler(
        PIDSpeedController(SpeedControl(kc=10, ki=0, kd=0), 100), driver
    )
    handler.set_measured_speeds(1.0, 0.0)
    handler.set_speeds(3.0, 2.0)
    assert bus.calls[-1] == ("write_block", 0x58, 0, [20, 20])
    handler.stop_motors()
    assert bus.calls[-1] == ("write_block", 0x58, 0, [0, 0])
    handler.reset()
    assert driver.prev_encoder_count_1 == 0
