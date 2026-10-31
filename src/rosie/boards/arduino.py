"""
The rosie motor driver shield on an Arduino, over a serial port
(firmware: github.com/PyForce/rosie-motordriver).
"""

import logging
import struct

from rosie.boards.models import ArduinoSettings
from rosie.buses import open_serial
from rosie.models import Profile, SerialPort
from rosie.motion.models import Clock, EncoderReading
from rosie.profile import read_table

logger = logging.getLogger(__name__)

COMMAND_SETPIDPARAM = 0xA6
COMMAND_SETPOINT = 0xA7
COMMAND_GETSTATE = b"\xa8"
COMMAND_GETSTATE_RESPONSE = b"\xa9"
COMMAND_ENCODER_RESET = b"\xaa"


class ArduinoBoard:
    """The shield controls the wheel speeds itself, with the profile's PID gains."""

    def __init__(self, serial_port: SerialPort) -> None:
        self.serial_port = serial_port
        self.battery_status = 100
        self.pulses_1 = 0
        self.pulses_2 = 0
        self.setpoint_1 = 0.0
        self.setpoint_2 = 0.0

    def set_speeds(
        self, speed_1: float, speed_2: float, _measured_1: float, _measured_2: float
    ) -> None:
        self.setpoint_1 = speed_1
        self.setpoint_2 = speed_2
        package = struct.pack("<Bff", COMMAND_SETPOINT, speed_2, speed_1)
        try:
            self.serial_port.write(package)
        except OSError:
            logger.exception("setting speeds")

    def stop(self) -> None:
        self.set_speeds(0.0, 0.0, 0.0, 0.0)

    def reset(self) -> None:
        pass

    def read_encoders(self) -> EncoderReading | None:
        try:
            self.serial_port.write(COMMAND_GETSTATE)
            if self.serial_port.read() != COMMAND_GETSTATE_RESPONSE:
                return None
            (pulses_1,) = struct.unpack("i", self.serial_port.read(4))
            (pulses_2,) = struct.unpack("i", self.serial_port.read(4))
            (battery_charge,) = struct.unpack("B", self.serial_port.read())
        except (OSError, struct.error):
            logger.exception("reading encoders")
            return 0, 0, 0, 0, 0
        delta_pulses_1 = pulses_1 - self.pulses_1
        delta_pulses_2 = pulses_2 - self.pulses_2
        self.pulses_1 = pulses_1
        self.pulses_2 = pulses_2
        self.battery_status = battery_charge
        # the shield counts the wheels the other way round
        return delta_pulses_2, delta_pulses_1, self.battery_status, 0, 0

    def set_constants(self, kc: float, ki: float, kd: float) -> None:
        package = struct.pack("<Bfff", COMMAND_SETPIDPARAM, kc, ki, kd)
        try:
            self.serial_port.write(package)
        except OSError:
            logger.exception("setting constants")

    def reset_encoders(self) -> None:
        try:
            self.serial_port.write(COMMAND_ENCODER_RESET)
        except OSError:
            logger.exception("resetting encoders")


def open_board(profile: Profile, _clock: Clock) -> ArduinoBoard:
    settings = read_table(ArduinoSettings, profile.board_settings, f"[board] of {profile.id}")
    board = ArduinoBoard(open_serial(settings.port, settings.baudrate))
    speed = profile.control.speed
    board.set_constants(speed.kc, speed.ki, speed.kd)
    return board
