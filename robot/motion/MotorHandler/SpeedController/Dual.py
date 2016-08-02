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

