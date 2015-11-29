# Script just for simulations. It allows to use rOSi platform without a robot.
# Author: Gustavo Viera Lopez

import math
import time
from robot import settings

# # Constants
# ENCODER_STEPS = 360
# MAX_SPEED = 20 # rad/sec



class VirtualMotorDriver:    
    def __init__(self):
        # Private variables (You should not access it directly, use methods instead)
        self.encoder1 = 0
        self.encoder2 = 0
        self.battery_voltage = 100
        self.history = []
        self.current_speed1 = 0
        self.current_speed2 = 0
        self.ENCODER_STEPS = settings.ENCODER_STEPS
        self.MAX_SPEED = settings.MAX_SPEED

    def set_speeds(self, motor1, motor2):
        self.current_speed1, self.current_speed2 = self.__check_max_speed__(motor1, motor2)
        self.history.append([self.current_speed1, self.current_speed2, time.time()])

    def read_state(self):
        self.history.append([self.current_speed1, self.current_speed2, time.time()])
        self.__update_encoders_status__() 
        # print(self.encoder1, self.encoder2)
        return self.encoder1, self.encoder2, self.battery_voltage

    def reset_encoders(self):
        self.encoder1 = 0
        self.encoder2 = 0
        self.current_speed1 = 0
        self.current_speed2 = 0
        self.history = []

    def __update_encoders_status__(self):
        delta_angle1 = 0
        delta_angle2 = 0

        for x in range(len(self.history) - 1):
            self.history[x][2] = self.history[x + 1][2] - self.history[x][2]
        self.history.__delitem__(-1)

        for x in range(len(self.history)):
            delta_angle1 += self.history[x][0] * self.history[x][2]
            delta_angle2 += self.history[x][1] * self.history[x][2]

        delta_steps1 = delta_angle1 / 2. / math.pi * self.ENCODER_STEPS
        delta_steps2 = delta_angle2 / 2. / math.pi * self.ENCODER_STEPS

        self.encoder1 += int(delta_steps1)
        self.encoder2 += int(delta_steps2)

        self.__reset_history__()

    def __reset_history__(self):
        self.history = []
        self.history.append([self.current_speed1, self.current_speed2, time.time()])

    def __check_max_speed__(self, motor1, motor2):
        speed1 = motor1
        speed2 = motor2
        if motor1 >= self.MAX_SPEED:
            speed1 = self.MAX_SPEED 
        if motor2 >= self.MAX_SPEED:
            speed2 = self.MAX_SPEED
        if motor1 <= -self.MAX_SPEED:
            speed1 = -self.MAX_SPEED 
        if motor2 <= -self.MAX_SPEED:
            speed2 = -self.MAX_SPEED
        return speed1, speed2

Board = VirtualMotorDriver