from abc import ABCMeta, abstractmethod
from Motion.MovementController.Differential import DifferentialDriveRobotLocation

__author__ = 'Silvio'


class DifferentialDriveOdometryLocalizer:
    """
    Abstract class to localize a differential drive mobile robot using odometry

    @param robot_parameters: Parameters of the robot
    @type robot_parameters: Motion.RobotParameters.DifferentialDriveRobotParameters
    """
    __metaclass__ = ABCMeta

    def __init__(self, robot_parameters):
        self.robot_parameters = robot_parameters
        self.location = DifferentialDriveRobotLocation()
        self.globalLocation = DifferentialDriveRobotLocation()

    @abstractmethod
    def update_location(self, delta_encoder_count_1, delta_encoder_count_2):
        """
        Update the robot's location

        @rtype : tuple
        @return: Updated local and global locations (DifferentialDriveRobotLocation, DifferentialDriveRobotLocation)
        @param delta_encoder_count_1: Count of wheel 1's encoder since last update
        @param delta_encoder_count_2: Count of wheel 2's encoder since last update
        @type delta_encoder_count_1: int
        @type delta_encoder_count_2: int
        """
        pass

    def reset_location(self):
        """
        Reset the robot's location

        """
        self.location.reset()

    def reset_global_location(self):
        """
        Reset the robot's global location

        """
        self.globalLocation.reset()
