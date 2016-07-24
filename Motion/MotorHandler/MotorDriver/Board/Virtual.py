import time
import math
from Motion.MotorHandler.MotorDriver.Dual import DualSpeedMotorDriver

__author__ = 'Silvio'


class VirtualMotorDriver(DualSpeedMotorDriver):
    """
    A class to represent a virtual robot

    @param steps_per_revolution: Encoders count in one wheel revolution
    @param max_speed: Maximum value of the speed of the motor
    """

    MOTOR_CURRENT = 0.
    BATTERY_VOLTAGE = 12.0

    def __init__(self, steps_per_revolution, max_speed):
        self.current_speed_1 = 0.
        self.current_speed_2 = 0.
        self.max_speed = max_speed
        self.steps_per_revolution = steps_per_revolution
        self.encoder_1 = 0
        self.encoder_2 = 0
        self.history = list()

    def set_speeds(self, speed_1, speed_2):
        self.current_speed_1, self.current_speed_2 = self.__check_max_speed__(speed_1, speed_2)
        self.history.append([self.current_speed_1, self.current_speed_2, time.time()])

    def read_delta_encoders_count_state(self):
        self.history.append([self.current_speed_1, self.current_speed_2, time.time()])
        delta_encoder_count_1, delta_encoder_count_2 = self.__update_encoders_status__()
        return delta_encoder_count_1, delta_encoder_count_2, VirtualMotorDriver.BATTERY_VOLTAGE, VirtualMotorDriver.MOTOR_CURRENT, VirtualMotorDriver.MOTOR_CURRENT

    def __check_max_speed__(self, motor_1, motor_2):
        speed1 = motor_1
        speed2 = motor_2
        if motor_1 >= self.max_speed:
            speed1 = self.max_speed
        if motor_2 >= self.max_speed:
            speed2 = self.max_speed
        if motor_1 <= -self.max_speed:
            speed1 = -self.max_speed
        if motor_2 <= -self.max_speed:
            speed2 = -self.max_speed
        return speed1, speed2

    def __update_encoders_status__(self):
        delta_angle1 = 0
        delta_angle2 = 0

        for x in range(len(self.history) - 1):
            self.history[x][2] = self.history[x + 1][2] - self.history[x][2]
        self.history.__delitem__(-1)

        for x in range(len(self.history)):
            delta_angle1 += self.history[x][0] * self.history[x][2]
            delta_angle2 += self.history[x][1] * self.history[x][2]

        delta_steps_1 = delta_angle1 / 2. / math.pi * self.steps_per_revolution
        delta_steps_2 = delta_angle2 / 2. / math.pi * self.steps_per_revolution

        self.encoder_1 += int(delta_steps_1)
        self.encoder_2 += int(delta_steps_2)

        self.__reset_history__()

        return delta_steps_1, delta_steps_2

    def __reset_history__(self):
        self.history = []
        self.history.append([self.current_speed_1, self.current_speed_2, time.time()])
