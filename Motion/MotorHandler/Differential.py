from abc import abstractmethod, ABCMeta

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
    @type speed_motor_driver: Motion.MotorDriver.DualSpeedMotorDriver
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
    @type power_motor_driver: Motion.MotorDriver.DualPowerMotorDriver
    @type speed_controller: Motion.SpeedController.DualSpeedController
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
