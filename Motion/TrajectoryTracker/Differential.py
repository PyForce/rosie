from abc import ABCMeta, abstractmethod

__author__ = 'Silvio'


class DifferentialDriveTrajectoryTracker:
    """
    Abstract class to make trajectory tracking of a differential drive mobile robot

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def track(self, reference_location, reference_speed, robot_location):
        """
        Method to determine the speed to drive the motors of the robot

        @rtype : tuple
        @return: speed of reference for the wheel (2 float) and corrected x and y speeds of reference (2 float)
        @param robot_location: actual robot's location
        @param reference_speed: speed of reference for the robot
        @param reference_location: location of reference for the robot
        @type robot_location: Motion.RobotLocation.DifferentialDriveRobotLocation
        @type reference_speed: Motion.RobotSpeed.DifferentialDriveRobotSpeed
        @type reference_location: Motion.RobotLocation.DifferentialDriveRobotLocation
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reset the tracker

        """
        pass
