from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

# a sensor's table in the profile -> the function reading it
type SensorFactory = Callable[[dict[str, Any]], Callable[[], object]]


@dataclass(frozen=True, slots=True)
class UltrasoundSettings:
    bus: int = 1  # I2C bus number
    address: int = 0x10
