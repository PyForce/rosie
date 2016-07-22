from abc import ABCMeta, abstractmethod

__author__ = 'Silvio'


class DualSpeedController:
    """
    Abstract class to make speed control for two motors

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def regulate(self, set_point_1, set_point_2, angular_speed_1, angular_speed_2):
        """
        Method to determine the powers to drive the motors

        @param angular_speed_1: actual angular speed of motor 1
        @param angular_speed_2: actual angular speed of motor 2
        @type angular_speed_2: float
        @type angular_speed_1: float
        @param set_point_2: actual angular speed of reference for motor 2
        @param set_point_1: actual angular speed of reference for motor 1
        @type set_point_2: float
        @type set_point_1: float
        @rtype : tuple
        @return: powers to drives the motors (2 float)
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reset the controller

        """
        pass


class PIDSpeedController(DualSpeedController):
    """
    Implementation of a PID controller to make control of the speed of two motors

    @param min_control_action: lower (saturation) value of the power
    @param max_control_action: higher (saturation) value of the power
    @param constant_kd: value of the kd constant of the PID controller
    @param constant_ki: value of the ki constant of the PID controller
    @param constant_kc: value of the kc constant of the PID controller
    @type min_control_action: float
    @type max_control_action: float
    @type constant_kd: float
    @type constant_ki: float
    @type constant_kc: float
    """
    def __init__(self, constant_kc, constant_ki, constant_kd, max_control_action, min_control_action):
        super(PIDSpeedController, self).__init__()
        self.min_control_action = min_control_action
        self.max_control_action = max_control_action
        self.constant_kd = constant_kd
        self.constant_ki = constant_ki
        self.constant_kc = constant_kc

        self.e1k1 = 0.
        self.e1k2 = 0.
        self.u1k1 = 0.

        self.e2k1 = 0.
        self.e2k2 = 0.
        self.u2k1 = 0.

    def reset(self):
        """
        Reset the controller

        """
        self.e1k1 = 0.
        self.e1k2 = 0.
        self.u1k1 = 0.

        self.e2k1 = 0.
        self.e2k2 = 0.
        self.u2k1 = 0.

    def regulate(self, set_point_1, set_point_2, angular_speed_1, angular_speed_2):
        """
        Method to determine the powers to drive the motors

        @param angular_speed_1: actual angular speed of motor 1
        @param angular_speed_2: actual angular speed of motor 2
        @type angular_speed_2: float
        @type angular_speed_1: float
        @param set_point_2: actual angular speed of reference for motor 2
        @param set_point_1: actual angular speed of reference for motor 1
        @type set_point_2: float
        @type set_point_1: float
        @rtype : tuple
        @return: powers to drives the motors (2 float)
        """
        e1k = set_point_1 - angular_speed_1

        if self.constant_ki == 0:
            uuu1 = e1k * self.constant_kc
        else:
            uuu1 = e1k * self.constant_kc + (self.constant_ki - self.constant_kc) * self.e1k1 + self.u1k1

        if self.constant_kd != 0:
            uuu1 = self.constant_kc * (e1k - self.e1k1) + self.constant_ki * e1k + self.u1k1 + self.constant_kd * (
                e1k - 2 * self.e1k1 + self.e1k2)

        if uuu1 > self.max_control_action:
            uuu1 = self.max_control_action
        if uuu1 < self.min_control_action:
            uuu1 = self.min_control_action

        self.u1k1 = uuu1
        self.e1k2 = self.e1k1
        self.e1k1 = e1k

        e2k = (set_point_2 - angular_speed_2)

        if self.constant_ki == 0:
            uuu2 = e2k * self.constant_kc
        else:
            uuu2 = e2k * self.constant_kc + (self.constant_ki - self.constant_kc) * self.e2k1 + self.u2k1

        if self.constant_kd != 0:
            uuu2 = self.constant_kc * (e2k - self.e2k1) + self.constant_ki * e2k + self.u2k1 + self.constant_kd * (
                e2k - 2 * self.e2k1 + self.e2k2)

        if uuu2 > self.max_control_action:
            uuu2 = self.max_control_action
        if uuu2 < self.min_control_action:
            uuu2 = self.min_control_action

        self.u2k1 = uuu2
        self.e2k2 = self.e2k1
        self.e2k1 = e2k

        return uuu1, uuu2
