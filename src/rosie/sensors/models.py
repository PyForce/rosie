from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UltrasoundSettings:
    bus: int = 1  # I2C bus number
    address: int = 0x10
