import math
from abc import ABC, abstractmethod

from rosie.motion.models import ORIGIN, Pose


class OdometryLocalizer(ABC):
    """
    Abstract class to localize a differential drive mobile robot using odometry

    @param robot_parameters: Parameters of the robot
    @type robot_parameters: motion.RobotParameters.RobotParameters
    """

    def __init__(self, robot_parameters):
        self.robot_parameters = robot_parameters
        self.location = ORIGIN
        self.global_location = ORIGIN

    @abstractmethod
    def update_location(self, delta_encoder_count_1, delta_encoder_count_2):
        """
        Update the robot's location

        @rtype : tuple
        @return: Updated local and global locations (Pose, Pose)
        @param delta_encoder_count_1: Count of wheel 1's encoder since last update
        @param delta_encoder_count_2: Count of wheel 2's encoder since last update
        @type delta_encoder_count_1: int
        @type delta_encoder_count_2: int
        """
        pass


class RungeKutta2Localizer(OdometryLocalizer):
    """
    Class to localize a differential drive mobile robot using odometry and Runge Kutta method

    @param robot_parameters: Parameters of the robot
    @type robot_parameters: motion.RobotParameters.RobotParameters
    """

    def __init__(self, robot_parameters):
        super().__init__(robot_parameters)
        self.prev_encoder_count_1 = 0
        self.prev_encoder_count_2 = 0
        self.prev_delta_encoder_1 = 0
        self.prev_delta_encoder_2 = 0
        self.encoder_count_1 = 0
        self.encoder_count_2 = 0

    def update_location(self, delta_encoder_count_1, delta_encoder_count_2):
        """
        Update the robot's location

        @rtype : Pose
        @return: Updated location
        @param delta_encoder_count_1: Count of wheel 1's encoder since last update
        @param delta_encoder_count_2: Count of wheel 2's encoder since last update
        @type delta_encoder_count_1: int
        @type delta_encoder_count_2: int
        """
        dfr = delta_encoder_count_2 * 2 * math.pi / self.robot_parameters.steps_per_revolution
        dfl = delta_encoder_count_1 * 2 * math.pi / self.robot_parameters.steps_per_revolution

        ds = (dfr + dfl) * self.robot_parameters.wheel_radius / 2
        dz = (dfr - dfl) * self.robot_parameters.wheel_radius / self.robot_parameters.wheel_distance

        self.location = _advance(self.location, ds, dz)
        self.global_location = _advance(self.global_location, ds, dz)
        return self.location, self.global_location


def _advance(pose: Pose, ds: float, dz: float) -> Pose:
    heading = pose.theta + dz / 2
    return Pose(pose.x + ds * math.cos(heading), pose.y + ds * math.sin(heading), pose.theta + dz)
