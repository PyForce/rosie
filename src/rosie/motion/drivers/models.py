from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VirtualBoard:
    """A simulated board: no settings."""


@dataclass(frozen=True, slots=True)
class ArduinoBoard:
    port: str = "/dev/ttyACM0"  # serial port
    baudrate: int = 9600


@dataclass(frozen=True, slots=True)
class MD25Board:
    bus: int = 1  # I2C bus number
    address: int = 0x58
    max_power: float = 127.0  # powers go from -max_power to max_power
