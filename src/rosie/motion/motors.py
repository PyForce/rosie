from abc import abstractmethod, ABCMeta
from abc import ABCMeta, abstractmethod

__author__ = 'Silvio'


class DifferentialDriveMotorHandler:
    """
    Abstract class representing a handler to control the motors of a differential drive robot

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def read_delta_encoders_count_state(self):
        """
        Reads the encoders count since last read and state of the motors

        @rtype : tuple
        @return: encoders count since last read (2 integers), battery voltage (float), motor's current (2 floats)
        """
        pass

    @abstractmethod
    def set_speeds(self, speed_1, speed_2):
        """
        Set the speeds to the motors

        @param speed_1: Speed for motor 1
        @param speed_2: Speed for motor 2
        @type speed_2: float
        @type speed_1: float
        """
        pass

    @abstractmethod
    def set_measured_speeds(self, measured_speed_1, measured_speed_2):
        """
        Set the feedback speeds of the motors

        @param measured_speed_1: Feedback speed for motor 1
        @param measured_speed_2: Feedback speed for motor 2
        @type measured_speed_2: float
        @type measured_speed_1: float
        """
        pass

    @abstractmethod
    def stop_motors(self):
        """
        Stop both motors

        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reset the handler

        """
        pass


class HardSpeedControlledMH(DifferentialDriveMotorHandler):
    """
    Class to handle the speed of motors using a driver that make control of the speeds directly

    @param speed_motor_driver: Driver to be used to set the speeds of the motors
    @type speed_motor_driver: motion.MotorDriver.DualSpeedMotorDriver
    """
    def __init__(self, speed_motor_driver):
        super(HardSpeedControlledMH, self).__init__()
        self.speed_motor_driver = speed_motor_driver

    def set_speeds(self, speed_1, speed_2):
        """
        Set the speeds to the motors

        @param speed_1: Speed for motor 1
        @param speed_2: Speed for motor 2
        @type speed_2: float
        @type speed_1: float
        """
        self.speed_motor_driver.set_speeds(speed_1, speed_2)

    def read_delta_encoders_count_state(self):
        """
        Reads the encoders count since last read and state of the motors

        @rtype : tuple
        @return: encoders count since last read (2 integers), battery voltage (float), motor's current (2 floats)
        """
        return self.speed_motor_driver.read_delta_encoders_count_state()

    def set_measured_speeds(self, measured_speed_1, measured_speed_2):
        """
        Set the feedback speeds of the motors

        @param measured_speed_1: Feedback speed for motor 1
        @param measured_speed_2: Feedback speed for motor 2
        @type measured_speed_2: float
        @type measured_speed_1: float
        """
        pass

    def stop_motors(self):
        """
        Stop both motors

        """
        self.set_speeds(0., 0.)

    def reset(self):
        """
        Reset the handler

        """
        pass


class SoftSpeedControlledMH(DifferentialDriveMotorHandler):
    """
    Class to handle the speed of motors using an speed controller

    @param speed_controller: Controller to be used to control the speeds of the motors
    @param power_motor_driver: Drive to be used to set the power of the motors
    @type power_motor_driver: motion.MotorDriver.DualPowerMotorDriver
    @type speed_controller: motion.SpeedController.DualSpeedController
    """

    def __init__(self, speed_controller, power_motor_driver):
        super(SoftSpeedControlledMH, self).__init__()
        self.power_motor_driver = power_motor_driver
        self.speed_controller = speed_controller

    def set_speeds(self, speed_1, speed_2):
        """
        Set the speeds to the motors

        @param speed_1: Speed for motor 1
        @param speed_2: Speed for motor 2
        @type speed_2: float
        @type speed_1: float
        """
        real_speed_1, real_speed_2 = self.power_motor_driver.get_real_speeds()
        control_action_1, control_action_2 = self.speed_controller.regulate(speed_1, speed_2, real_speed_1,
                                                                            real_speed_2)
        self.power_motor_driver.set_powers(control_action_1, control_action_2)

    def read_delta_encoders_count_state(self):
        """
        Reads the encoders count since last read and state of the motors

        @rtype : tuple
        @return: encoders count since last read (2 integers), battery voltage (float), motor's current (2 floats)
        """
        return self.power_motor_driver.read_delta_encoders_count_state()

    def set_measured_speeds(self, measured_speed_1, measured_speed_2):
        """
        Set the feedback speeds of the motors

        @param measured_speed_1: Feedback speed for motor 1
        @param measured_speed_2: Feedback speed for motor 2
        @type measured_speed_2: float
        @type measured_speed_1: float
        """
        self.power_motor_driver.set_real_speeds(measured_speed_1, measured_speed_2)

    def stop_motors(self):
        """
        Stop both motors

        """
        self.power_motor_driver.set_powers(0., 0.)

    def reset(self):
        """
        Reset the handler

        """
        self.speed_controller.reset()
        self.power_motor_driver.reset()


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
