import math
from abc import ABC, abstractmethod


class TrajectoryTracker(ABC):
    """
    Abstract class to make trajectory tracking of a differential drive mobile robot

    """

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
        @type robot_location: motion.RobotLocation.Pose
        @type reference_speed: motion.RobotSpeed.Velocity
        @type reference_location: motion.RobotLocation.Pose
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reset the tracker

        """
        pass


class IOLinearizationTracker(TrajectoryTracker):
    """
    Class to make trajectory tracking of a differential drive mobile robot using IO Linearization Method

    @param robot_parameters: parameters of the robot
    @param constant_k2: constant k2 of the tracker
    @param constant_k1: constant k1 of the tracker
    @param constant_b: constant b of the tracker
    @param smooth_flag: don't use P point as reference("smooth control")
    @type robot_parameters: motion.RobotParameters.RobotParameters
    @type constant_k2: float
    @type constant_k1: float
    @type constant_b: float
    @type smooth_flag: bool
    """

    def __init__(self, robot_parameters, smooth_flag=False):
        super().__init__()
        self.robot_parameters = robot_parameters
        self.constant_k2 = robot_parameters.constant_k2
        self.constant_k1 = robot_parameters.constant_k1
        self.constant_b = robot_parameters.constant_b
        self.smooth_flag = smooth_flag

    def reset(self):
        """
        Reset the tracker

        """
        pass

    def track(self, reference_location, reference_speed, robot_location):
        """
        Method to determine the speed to drive the motors of the robot

        @rtype : tuple
        @return: speed of reference for the wheel (2 float) and corrected x and y speeds of reference (2 float)
        @param robot_location: actual robot's location
        @param reference_speed: speed of reference for the robot
        @param reference_location: location of reference for the robot
        @type robot_location: motion.RobotLocation.Pose
        @type reference_speed: motion.RobotSpeed.Velocity
        @type reference_location: motion.RobotLocation.Pose
        """
        xd = reference_location.x
        yd = reference_location.y
        zd = reference_location.theta

        xd_dot = reference_speed.x
        yd_dot = reference_speed.y
        zd_dot = reference_speed.theta

        y1 = robot_location.x + self.constant_b * math.cos(robot_location.theta)
        y2 = robot_location.y + self.constant_b * math.sin(robot_location.theta)

        if self.smooth_flag:
            y1d = reference_location.x
            y2d = reference_location.y

            y1d_dot = reference_speed.x
            y2d_dot = reference_speed.y
        else:
            y1d = xd + self.constant_b * math.cos(zd)
            y2d = yd + self.constant_b * math.sin(zd)

            y1d_dot = xd_dot - self.constant_b * math.sin(zd) * zd_dot
            y2d_dot = yd_dot + self.constant_b * math.cos(zd) * zd_dot

        u2 = y2d_dot + self.constant_k2 * (y2d - y2)
        u1 = y1d_dot + self.constant_k1 * (y1d - y1)

        the_v = math.cos(robot_location.theta) * u1 + u2 * math.sin(robot_location.theta)
        the_omega = (
            u1 * (-math.sin(robot_location.theta) / self.constant_b)
            + u2 * math.cos(robot_location.theta) / self.constant_b
        )

        set_point_2 = (
            the_v / self.robot_parameters.wheel_radius
            + the_omega
            * self.robot_parameters.wheel_distance
            / 2
            / self.robot_parameters.wheel_radius
        )
        set_point_1 = (
            the_v / self.robot_parameters.wheel_radius
            - the_omega
            * self.robot_parameters.wheel_distance
            / 2
            / self.robot_parameters.wheel_radius
        )

        return set_point_1, set_point_2, u1, u2
