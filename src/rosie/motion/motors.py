from abc import ABC, abstractmethod

from rosie.motion.drivers.base import PowerMotorDriver, SpeedMotorDriver
from rosie.motion.models import EncoderReading, PIDHistory, SpeedControl


class SpeedController(ABC):
    @abstractmethod
    def regulate(
        self, set_point_1: float, set_point_2: float, angular_speed_1: float, angular_speed_2: float
    ) -> tuple[float, float]:
        """Powers for both motors, to bring their speeds to the set points."""

    @abstractmethod
    def reset(self) -> None: ...


class PIDSpeedController(SpeedController):
    def __init__(self, speed: SpeedControl, max_power: float) -> None:
        """Powers go from -max_power to max_power."""
        self.max_power = max_power
        self.kd = speed.kd
        self.ki = speed.ki
        self.kc = speed.kc
        self._wheel_1 = PIDHistory(0.0, 0.0, 0.0)
        self._wheel_2 = PIDHistory(0.0, 0.0, 0.0)

    def reset(self) -> None:
        self._wheel_1 = PIDHistory(0.0, 0.0, 0.0)
        self._wheel_2 = PIDHistory(0.0, 0.0, 0.0)

    def regulate(
        self, set_point_1: float, set_point_2: float, angular_speed_1: float, angular_speed_2: float
    ) -> tuple[float, float]:
        return (
            self._regulate(self._wheel_1, set_point_1 - angular_speed_1),
            self._regulate(self._wheel_2, set_point_2 - angular_speed_2),
        )

    def _regulate(self, wheel: PIDHistory, error: float) -> float:
        if self.ki == 0:
            action = error * self.kc
        else:
            action = error * self.kc + (self.ki - self.kc) * wheel.error_1 + wheel.action_1

        if self.kd != 0:
            action = (
                self.kc * (error - wheel.error_1)
                + self.ki * error
                + wheel.action_1
                + self.kd * (error - 2 * wheel.error_1 + wheel.error_2)
            )

        action = min(max(action, -self.max_power), self.max_power)

        wheel.action_1 = action
        wheel.error_2 = wheel.error_1
        wheel.error_1 = error
        return action


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
