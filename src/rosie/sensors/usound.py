"""
Ultrasound board: 12 ultrasonic range sensors and an LM35 thermometer behind a
microcontroller on the I2C bus.

Every command is sent twice, then its arguments. Status register 1 holds the
global enable (bit 0), the LM35 (bit 1) and sensors 1 to 5 (bits 2 to 6);
status register 2 is marked by bit 7 and holds sensors 6 to 12 (bits 0 to 6).
"""

import logging
import time
from collections.abc import Callable

from rosie.motion.drivers.buses import I2CBus, open_i2c
from rosie.profile import Ultrasound
from rosie.robot import Robot

logger = logging.getLogger(__name__)

SENSORS = 12
SENSORS_IN_REGISTER_1 = 5
DEFAULT_ADDRESS = 0x10
SPEED_OF_SOUND = 347.8  # m/s at the default temperature
DEFAULT_TEMPERATURE = 28.0  # °C, used while the LM35 is off
MIN_PERIOD_MS = 60
MAX_ADDRESS = 0x77
ATTEMPTS = 6  # one try and five retries on I2C errors
RETRY_PAUSE = 0.5  # s

CHANGE_ADDRESS = 0x01
READ_TEMPERATURE = 0x02
SET_PERIOD = 0x03
GET_PERIOD = 0x04
SET_STATUS = 0x05
GET_STATUS = 0x06
RESET = 0x08
READ_SENSOR = 0x08  # + sensor number (1 to 12)

GLOBAL_BIT = 0x01
LM35_BIT = 0x02
SECOND_REGISTER = 0x80

# measured distance (cm) up to which each correction applies, and the correction
CORRECTIONS = ((10, 0.1), (20, 0.06), (30, 0.03), (40, 0.04), (float("inf"), 0.02))


def attach(robot: Robot, settings: Ultrasound) -> None:
    """Open the board and serve its readings as the robot's `usound` sensor."""
    board = UltrasoundBoard(open_i2c(settings.bus), settings.address)
    robot.sensors["usound"] = board.read_all


class UltrasoundBoard:
    def __init__(self, bus: I2CBus, address: int) -> None:
        self.bus = bus
        self.address = address
        self.status_1 = 0x00
        self.status_2 = SECOND_REGISTER
        self.period_ms = 60
        self.temperature = DEFAULT_TEMPERATURE
        self.speed_of_sound = SPEED_OF_SOUND

    def read_all(self) -> list[float | None]:
        """Switch every sensor on and read their distances (cm, corrected)."""
        self.enable_lm35()
        self.enable()
        for sensor in range(1, SENSORS + 1):
            self.enable_sensor(sensor)
        return [self.read_distance(sensor, corrected=True) for sensor in range(1, SENSORS + 1)]

    def read_distance(self, sensor: int, *, corrected: bool) -> float | None:
        """Distance in cm, or None if the sensor is off or can't be read."""
        if not (self.status_1 & GLOBAL_BIT and self._sensor_bit(sensor)):
            return None
        reading = self._retry(lambda: self._query(READ_SENSOR + sensor, 2))
        if reading is None:
            return None
        low, high = reading
        if corrected:
            return _correct(_distance_cm((high << 8) | low, self.speed_of_sound))
        return _distance_cm((high << 8) | low, SPEED_OF_SOUND)

    def read_temperature(self) -> float:
        """°C from the LM35, or the last known temperature while it's off."""
        if not (self.status_1 & LM35_BIT and self.status_1 & GLOBAL_BIT):
            logger.warning("the LM35 or the board is off, using %s °C", self.temperature)
            return round(self.temperature, 2)
        reading = self._retry(lambda: self._query(READ_TEMPERATURE, 2))
        if reading is None:
            return round(self.temperature, 2)
        low, high = reading
        return round(((high << 8) | low) * 50.0 / 1023.0, 2)

    def calibrate(self, samples: int) -> None:
        """Average the LM35 and adjust the speed of sound to the temperature."""
        readings = []
        for _ in range(samples):
            readings.append(self.read_temperature())
            time.sleep(0.1)
        self.temperature = round(sum(readings) / samples, 2)
        self.speed_of_sound = round(self.temperature * 0.6 + 331, 2)

    def enable(self) -> None:
        self.set_status(self.status_1 | GLOBAL_BIT)

    def disable(self) -> None:
        self.set_status(self.status_1 & ~GLOBAL_BIT & 0xFF)

    def enable_lm35(self) -> None:
        self.set_status(self.status_1 | LM35_BIT)

    def disable_lm35(self) -> None:
        self.set_status(self.status_1 & ~LM35_BIT & 0xFF)

    def enable_sensor(self, sensor: int) -> None:
        register, bit = self._sensor_position(sensor)
        self.set_status(register | bit)

    def disable_sensor(self, sensor: int) -> None:
        register, bit = self._sensor_position(sensor)
        self.set_status(register & ~bit & 0xFF)

    def set_status(self, value: int) -> None:
        if value & SECOND_REGISTER:
            self.status_2 = value
        else:
            self.status_1 = value
        self._retry(lambda: self._command(SET_STATUS, value))

    def read_status(self) -> None:
        reading = self._retry(lambda: self._query(GET_STATUS, 2))
        if reading is not None:
            self.status_1, self.status_2 = reading

    def set_period(self, period_ms: int) -> None:
        """Time between two measurements of the board, at least 60 ms."""
        if period_ms < MIN_PERIOD_MS:
            raise ValueError(f"the period must be at least {MIN_PERIOD_MS} ms")
        low, high = period_ms & 0xFF, (period_ms >> 8) & 0xFF
        self._retry(lambda: self._command(SET_PERIOD, low, high))
        self.period_ms = (high << 8) | low

    def read_period(self) -> None:
        reading = self._retry(lambda: self._query(GET_PERIOD, 2))
        if reading is not None:
            low, high = reading
            self.period_ms = (high << 8) | low

    def change_address(self, address: int) -> None:
        if address > MAX_ADDRESS:
            raise ValueError(f"the address must be at most {MAX_ADDRESS:#x}")
        self._retry(lambda: self._command(CHANGE_ADDRESS, address))
        self.address = address

    def reset(self) -> None:
        """Reset the board and give it back its address, status and period."""
        self._retry(lambda: self._command(RESET))
        address, self.address = self.address, DEFAULT_ADDRESS
        self.change_address(address)
        self.set_status(self.status_1)
        self.set_status(self.status_2)
        self.set_period(self.period_ms)

    def _sensor_bit(self, sensor: int) -> int:
        register, bit = self._sensor_position(sensor)
        return register & bit

    def _sensor_position(self, sensor: int) -> tuple[int, int]:
        """The status register holding the sensor's bit, and the bit."""
        if not 1 <= sensor <= SENSORS:
            raise ValueError(f"the sensors are numbered 1 to {SENSORS}")
        if sensor <= SENSORS_IN_REGISTER_1:
            return self.status_1, 1 << (1 + sensor)
        return self.status_2, 1 << (sensor - 6)

    def _command(self, operation: int, *arguments: int) -> None:
        self.bus.write_byte(self.address, operation)
        self.bus.write_byte(self.address, operation)
        for argument in arguments:
            self.bus.write_byte(self.address, argument)

    def _query(self, operation: int, count: int) -> list[int]:
        self._command(operation)
        return [self.bus.read_byte(self.address) for _ in range(count)]

    def _retry[T](self, action: Callable[[], T]) -> T | None:
        for attempt in range(1, ATTEMPTS + 1):
            try:
                return action()
            except OSError:
                logger.warning(
                    "I2C error on the ultrasound board (try %d of %d)", attempt, ATTEMPTS
                )
                time.sleep(RETRY_PAUSE)
        logger.error("the ultrasound board doesn't answer, please check the connection")
        return None


def _distance_cm(ticks: int, speed_of_sound: float) -> float:
    return round(ticks * 0.17 * speed_of_sound / 10000, 2)


def _correct(distance: float) -> float:
    correction = next(correction for limit, correction in CORRECTIONS if distance <= limit)
    return round(distance - distance * correction, 2)
