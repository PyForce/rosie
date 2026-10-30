from abc import ABC, abstractmethod
from dataclasses import dataclass

from rosie.motion.drivers.base import PowerMotorDriver, SpeedMotorDriver
from rosie.motion.models import EncoderReading


class MotorHandler(ABC):
    @abstractmethod
    def read_delta_encoders_count_state(self) -> EncoderReading | None: ...

    @abstractmethod
    def set_speeds(self, speed_1: float, speed_2: float) -> None: ...

    @abstractmethod
    def set_measured_speeds(self, measured_speed_1: float, measured_speed_2: float) -> None: ...

    @abstractmethod
    def stop_motors(self) -> None: ...

    @abstractmethod
    def reset(self) -> None: ...


class HardwareSpeedMotorHandler(MotorHandler):
    """For boards that control the wheel speeds themselves."""

    def __init__(self, speed_motor_driver: SpeedMotorDriver) -> None:
        self.speed_motor_driver = speed_motor_driver

    def set_speeds(self, speed_1: float, speed_2: float) -> None:
        self.speed_motor_driver.set_speeds(speed_1, speed_2)

    def read_delta_encoders_count_state(self) -> EncoderReading | None:
        return self.speed_motor_driver.read_delta_encoders_count_state()

    def set_measured_speeds(self, measured_speed_1: float, measured_speed_2: float) -> None:
        pass

    def stop_motors(self) -> None:
        self.set_speeds(0.0, 0.0)

    def reset(self) -> None:
        pass


class SoftwareSpeedMotorHandler(MotorHandler):
    """For boards that only set motor power: rosie controls the speeds."""

    def __init__(
        self, speed_controller: SpeedController, power_motor_driver: PowerMotorDriver
    ) -> None:
        self.power_motor_driver = power_motor_driver
        self.speed_controller = speed_controller

    def set_speeds(self, speed_1: float, speed_2: float) -> None:
        real_speed_1, real_speed_2 = self.power_motor_driver.get_real_speeds()
        control_action_1, control_action_2 = self.speed_controller.regulate(
            speed_1, speed_2, real_speed_1, real_speed_2
        )
        self.power_motor_driver.set_powers(control_action_1, control_action_2)

    def read_delta_encoders_count_state(self) -> EncoderReading | None:
        return self.power_motor_driver.read_delta_encoders_count_state()

    def set_measured_speeds(self, measured_speed_1: float, measured_speed_2: float) -> None:
        self.power_motor_driver.set_real_speeds(measured_speed_1, measured_speed_2)

    def stop_motors(self) -> None:
        self.power_motor_driver.set_powers(0.0, 0.0)

    def reset(self) -> None:
        self.speed_controller.reset()
        self.power_motor_driver.reset()


class SpeedController(ABC):
    @abstractmethod
    def regulate(
        self, set_point_1: float, set_point_2: float, angular_speed_1: float, angular_speed_2: float
    ) -> tuple[float, float]:
        """Powers for both motors, to bring their speeds to the set points."""

    @abstractmethod
    def reset(self) -> None: ...


class PIDSpeedController(SpeedController):
    def __init__(
        self,
        constant_kc: float,
        constant_ki: float,
        constant_kd: float,
        max_control_action: float,
        min_control_action: float,
    ) -> None:
        self.min_control_action = min_control_action
        self.max_control_action = max_control_action
        self.constant_kd = constant_kd
        self.constant_ki = constant_ki
        self.constant_kc = constant_kc
        self._wheel_1 = _WheelHistory(0.0, 0.0, 0.0)
        self._wheel_2 = _WheelHistory(0.0, 0.0, 0.0)

    def reset(self) -> None:
        self._wheel_1 = _WheelHistory(0.0, 0.0, 0.0)
        self._wheel_2 = _WheelHistory(0.0, 0.0, 0.0)

    def regulate(
        self, set_point_1: float, set_point_2: float, angular_speed_1: float, angular_speed_2: float
    ) -> tuple[float, float]:
        return (
            self._regulate(self._wheel_1, set_point_1 - angular_speed_1),
            self._regulate(self._wheel_2, set_point_2 - angular_speed_2),
        )

    def _regulate(self, wheel: _WheelHistory, error: float) -> float:
        if self.constant_ki == 0:
            action = error * self.constant_kc
        else:
            action = (
                error * self.constant_kc
                + (self.constant_ki - self.constant_kc) * wheel.error_1
                + wheel.action_1
            )

        if self.constant_kd != 0:
            action = (
                self.constant_kc * (error - wheel.error_1)
                + self.constant_ki * error
                + wheel.action_1
                + self.constant_kd * (error - 2 * wheel.error_1 + wheel.error_2)
            )

        action = min(max(action, self.min_control_action), self.max_control_action)

        wheel.action_1 = action
        wheel.error_2 = wheel.error_1
        wheel.error_1 = error
        return action


@dataclass(slots=True)
class _WheelHistory:
    error_1: float  # error one step ago
    error_2: float  # error two steps ago
    action_1: float  # control action one step ago
