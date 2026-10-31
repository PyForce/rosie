from abc import ABC, abstractmethod

from rosie.motion.models import EncoderReading


class MotorDriver(ABC):
    """A board driving the robot's two motors."""

    @abstractmethod
    def read_encoders(self) -> EncoderReading | None: ...


class SpeedMotorDriver(MotorDriver):
    """A board that takes wheel speeds and controls them itself."""

    @abstractmethod
    def set_speeds(self, speed_1: float, speed_2: float) -> None: ...


class PowerMotorDriver(MotorDriver):
    """A board that only takes motor powers: rosie controls the speeds."""

    def __init__(self) -> None:
        self.real_speed_1 = 0.0
        self.real_speed_2 = 0.0

    @abstractmethod
    def set_powers(self, power_1: float, power_2: float) -> None: ...

    @abstractmethod
    def reset(self) -> None: ...

    def set_measured_speeds(self, real_speed_1: float, real_speed_2: float) -> None:
        self.real_speed_1 = real_speed_1
        self.real_speed_2 = real_speed_2

    def measured_speeds(self) -> tuple[float, float]:
        return self.real_speed_1, self.real_speed_2
