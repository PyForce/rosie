from abc import ABCMeta, abstractmethod

__author__ = 'Silvio'


class DifferentialDriveTrajectoryTracker:
    """
    Abstract class to make trajectory tracking of a differential drive mobile robotNew

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def track(self, reference_location, reference_speed, robot_location):
        """
        Method to determine the speed to drive the motors of the robotNew

        @rtype : tuple
        @return: speed of reference for the wheel (2 float) and corrected x and y speeds of reference (2 float)
        @param robot_location: actual robotNew's location
        @param reference_speed: speed of reference for the robotNew
        @param reference_location: location of reference for the robotNew
        @type robot_location: motion.RobotLocation.DifferentialDriveRobotLocation
        @type reference_speed: motion.RobotSpeed.DifferentialDriveRobotSpeed
        @type reference_location: motion.RobotLocation.DifferentialDriveRobotLocation
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reset the tracker

        """
        pass
