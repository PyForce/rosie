import math
from collections.abc import Callable
from itertools import pairwise

from rosie.motion.drivers.base import SpeedMotorDriver
from rosie.motion.models import EncoderReading

MOTOR_CURRENT = 0.0  # A
BATTERY_VOLTAGE = 12.0  # V


class VirtualMotorDriver(SpeedMotorDriver):
    """
    A simulated board: the wheels turn exactly at the speeds asked, and the
    encoders count what they turned between two readings.
    """

    def __init__(
        self, steps_per_revolution: float, max_speed: float, clock: Callable[[], float]
    ) -> None:
        self.current_speed_1 = 0.0
        self.current_speed_2 = 0.0
        self.max_speed = max_speed
        self.steps_per_revolution = steps_per_revolution
        self.clock = clock
        # (speed 1, speed 2, since when) for every speed change since the last reading
        self.history: list[tuple[float, float, float]] = []

    def set_speeds(self, speed_1: float, speed_2: float) -> None:
        self.current_speed_1 = self._clamp(speed_1)
        self.current_speed_2 = self._clamp(speed_2)
        self.history.append((self.current_speed_1, self.current_speed_2, self.clock()))

    def read_delta_encoders_count_state(self) -> EncoderReading:
        self.history.append((self.current_speed_1, self.current_speed_2, self.clock()))
        delta_steps_1, delta_steps_2 = self._integrate()
        self.history = [(self.current_speed_1, self.current_speed_2, self.clock())]
        return delta_steps_1, delta_steps_2, BATTERY_VOLTAGE, MOTOR_CURRENT, MOTOR_CURRENT

    def _clamp(self, speed: float) -> float:
        if speed >= self.max_speed:
            return self.max_speed
        if speed <= -self.max_speed:
            return -self.max_speed
        return speed

    def _integrate(self) -> tuple[float, float]:
        delta_angle_1 = 0.0
        delta_angle_2 = 0.0
        for (speed_1, speed_2, start), (_, _, end) in pairwise(self.history):
            delta_angle_1 += speed_1 * (end - start)
            delta_angle_2 += speed_2 * (end - start)
        return (
            delta_angle_1 / 2.0 / math.pi * self.steps_per_revolution,
            delta_angle_2 / 2.0 / math.pi * self.steps_per_revolution,
        )
