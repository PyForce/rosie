from rosie.motion.models import PIDHistory, SpeedControl


class PIDSpeedController:
    """The wheel speed PID, in its incremental form: powers for both motors from the speed errors."""

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
