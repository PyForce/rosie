"""The MD25 motor controller board, over the I2C bus."""

import importlib
import logging

from rosie.errors import HardwareUnavailableError
from rosie.motion.drivers.base import PowerMotorDriver
from rosie.motion.models import EncoderReading

logger = logging.getLogger(__name__)

# a jump larger than this between two readings is a glitch: the previous delta is used instead
MAX_ENCODER_COUNT_DELTA = 180
# the encoders are reset before they get anywhere near overflowing
MAX_ENCODER_COUNT = 2000000000
MAX_INT_32 = 2**31


class MD25MotorDriver(PowerMotorDriver):
    def __init__(self, i2c_bus_number: int, i2c_bus_address: int) -> None:
        super().__init__()
        try:
            # only robots with this board need smbus
            smbus = importlib.import_module("smbus")
        except ModuleNotFoundError as error:
            raise HardwareUnavailableError("the MD25 motor driver needs smbus") from error
        try:
            self.i2c_bus = smbus.SMBus(i2c_bus_number)
        except OSError as error:
            raise HardwareUnavailableError(f"no I2C bus {i2c_bus_number}") from error
        self.i2c_bus_address = i2c_bus_address
        self.prev_encoder_count_1 = 0
        self.prev_encoder_count_2 = 0
        self.encoder_count_1 = 0
        self.encoder_count_2 = 0
        self.prev_delta_encoder_count_1 = 0
        self.prev_delta_encoder_count_2 = 0
        self.reset_encoders()
        self.i2c_bus.write_byte_data(self.i2c_bus_address, 15, 1)
        self.i2c_bus.write_byte_data(self.i2c_bus_address, 16, 48)
        self.i2c_bus.write_byte_data(self.i2c_bus_address, 14, 10)

    def set_powers(self, power_1: float, power_2: float) -> None:
        self.i2c_bus.write_i2c_block_data(self.i2c_bus_address, 0, [int(power_1), int(power_2)])

    def read_delta_encoders_count_state(self) -> EncoderReading:
        encoder_count_1, encoder_count_2, battery_voltage, current_left, current_right = (
            self._read_state()
        )

        delta_encoder_count_1 = encoder_count_1 - self.prev_encoder_count_1
        delta_encoder_count_2 = encoder_count_2 - self.prev_encoder_count_2

        self.encoder_count_1 = encoder_count_1
        self.encoder_count_2 = encoder_count_2

        if abs(delta_encoder_count_1) > MAX_ENCODER_COUNT_DELTA:
            logger.info(
                "encoder 1 jumped %d steps, using %d",
                delta_encoder_count_1,
                self.prev_delta_encoder_count_1,
            )
            delta_encoder_count_1 = self.prev_delta_encoder_count_1
            self.encoder_count_1 = 0
            self.encoder_count_2 = 0
            self.reset_encoders()

        if abs(delta_encoder_count_2) > MAX_ENCODER_COUNT_DELTA:
            logger.info(
                "encoder 2 jumped %d steps, using %d",
                delta_encoder_count_2,
                self.prev_delta_encoder_count_2,
            )
            delta_encoder_count_2 = self.prev_delta_encoder_count_2
            self.encoder_count_1 = 0
            self.encoder_count_2 = 0
            self.reset_encoders()

        if abs(encoder_count_1) > MAX_ENCODER_COUNT or abs(encoder_count_2) > MAX_ENCODER_COUNT:
            logger.info("encoders reset before overflowing")
            self.encoder_count_1 = 0
            self.encoder_count_2 = 0
            self.reset_encoders()

        self.prev_encoder_count_1 = self.encoder_count_1
        self.prev_encoder_count_2 = self.encoder_count_2

        self.prev_delta_encoder_count_1 = delta_encoder_count_1
        self.prev_delta_encoder_count_2 = delta_encoder_count_2

        return (
            delta_encoder_count_1,
            delta_encoder_count_2,
            battery_voltage,
            current_left,
            current_right,
        )

    def reset(self) -> None:
        self.prev_encoder_count_1 = 0
        self.prev_encoder_count_2 = 0
        self.encoder_count_1 = 0
        self.encoder_count_2 = 0
        self.prev_delta_encoder_count_1 = 0
        self.prev_delta_encoder_count_2 = 0
        self.reset_encoders()

    def reset_encoders(self) -> None:
        self.i2c_bus.write_byte_data(self.i2c_bus_address, 16, 32)

    def _read_state(self) -> tuple[int, int, float, float, float]:
        result = self.i2c_bus.read_i2c_block_data(self.i2c_bus_address, 2, 11)

        encoder_1 = (result[0] << 24) + (result[1] << 16) + (result[2] << 8) + result[3]
        if encoder_1 > MAX_INT_32:
            encoder_1 = -(2**32 - encoder_1)

        encoder_2 = (result[4] << 24) + (result[5] << 16) + (result[6] << 8) + result[7]
        if encoder_2 > MAX_INT_32:
            encoder_2 = -(2**32 - encoder_2)

        battery_voltage = result[8] / float(10)
        current_left = result[9] / float(10)
        current_right = result[10] / float(10)

        return encoder_1, encoder_2, battery_voltage, current_left, current_right
