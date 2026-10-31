"""The MD25 motor controller board, over the I2C bus."""

import logging

from rosie.boards.models import MD25Settings
from rosie.buses import open_i2c
from rosie.models import I2CBus, Profile
from rosie.motion.models import Clock, EncoderReading, SpeedControl
from rosie.motion.pid import RESTING_PID, pid
from rosie.profile import read_table

logger = logging.getLogger(__name__)

# a jump larger than this between two readings is a glitch: the previous delta is used instead
MAX_ENCODER_COUNT_DELTA = 180
# the encoders are reset before they get anywhere near overflowing
MAX_ENCODER_COUNT = 2000000000
MAX_INT_32 = 2**31


class MD25Board:
    """The board only takes motor powers: rosie's PID turns the wheel speeds into them."""

    def __init__(
        self, i2c_bus: I2CBus, i2c_bus_address: int, gains: SpeedControl, max_power: float
    ) -> None:
        self.gains = gains
        self.max_power = max_power
        self.pid_1 = RESTING_PID
        self.pid_2 = RESTING_PID
        self.i2c_bus = i2c_bus
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

    def set_speeds(
        self, speed_1: float, speed_2: float, measured_1: float, measured_2: float
    ) -> None:
        power_1, self.pid_1 = pid(self.gains, self.max_power, self.pid_1, speed_1 - measured_1)
        power_2, self.pid_2 = pid(self.gains, self.max_power, self.pid_2, speed_2 - measured_2)
        self.set_powers(power_1, power_2)

    def stop(self) -> None:
        self.set_powers(0.0, 0.0)

    def set_powers(self, power_1: float, power_2: float) -> None:
        self.i2c_bus.write_i2c_block_data(self.i2c_bus_address, 0, [int(power_1), int(power_2)])

    def read_encoders(self) -> EncoderReading:
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
        self.pid_1 = RESTING_PID
        self.pid_2 = RESTING_PID
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


def open_board(profile: Profile, _clock: Clock) -> MD25Board:
    settings = read_table(MD25Settings, profile.board_settings, f"[board] of {profile.id}")
    return MD25Board(
        open_i2c(settings.bus), settings.address, profile.control.speed, settings.max_power
    )
