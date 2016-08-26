from abc import ABCMeta, abstractmethod

__author__ = 'Silvio'


class DualMotorDriver:
    """
    Abstract class representing a driver used to control 2 motors

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


class DualSpeedMotorDriver(DualMotorDriver):
    """
    Abstract class representing a driver used to control 2 motors using their speeds

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        super(DualSpeedMotorDriver, self).__init__()

    @abstractmethod
    def set_speeds(self, speed_1, speed_2):
        """
        Method to set the speed for each motor

        @type speed_2: float
        @type speed_1: float
        @param speed_1: Speed for motor 1
        @param speed_2: Speed for motor 2
        """
        pass


class DualPowerMotorDriver(DualMotorDriver):
    """
    Abstract class representing a driver used to control 2 motors using their powers

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        super(DualPowerMotorDriver, self).__init__()
        self.real_speed_1 = 0.
        self.real_speed_2 = 0.

    @abstractmethod
    def set_powers(self, power_1, power_2):
        """
        Method to set the power for each motor

        @type power_2: float
        @type power_1: float
        @param power_1: Power for motor 1
        @param power_2: Power for motor 2
        """
        pass

    def set_real_speeds(self, real_speed_1, real_speed_2):
        """
        Method to set the real speed of the motors

        @type real_speed_2: float
        @type real_speed_1: float
        @param real_speed_1: Speed for motor 1
        @param real_speed_2: Speed for motor 2
        """
        self.real_speed_1 = real_speed_1
        self.real_speed_2 = real_speed_2

    def get_real_speeds(self):
        """
        Method to get the real speed of the motors

        @rtype : tuple
        @return : Two floats with the real speed for both motors
        """
        return self.real_speed_1, self.real_speed_2

    @abstractmethod
    def reset(self):
        """
        Reset the driver

        """
        pass
