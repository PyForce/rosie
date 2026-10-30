import math
from abc import ABC, abstractmethod

from rosie.motion.models import Pose, RobotParameters, Velocity

# wheel 1 and 2 speed setpoints (rad/s), then the x and y speeds the tracker asked for
type TrackerOutput = tuple[float, float, float, float]


class TrajectoryTracker(ABC):
    @abstractmethod
    def track(self, reference: Pose, reference_velocity: Velocity, pose: Pose) -> TrackerOutput: ...

    @abstractmethod
    def reset(self) -> None: ...


class IOLinearizationTracker(TrajectoryTracker):
    """Input-output linearization: tracks a point at distance b ahead of the wheel axis."""

    def __init__(self, robot_parameters: RobotParameters) -> None:
        self.robot_parameters = robot_parameters
        self.constant_k2 = robot_parameters.constant_k2
        self.constant_k1 = robot_parameters.constant_k1
        self.constant_b = robot_parameters.constant_b

    def reset(self) -> None:
        pass

    def track(self, reference: Pose, reference_velocity: Velocity, pose: Pose) -> TrackerOutput:
        xd = reference.x
        yd = reference.y
        zd = reference.theta

        xd_dot = reference_velocity.x
        yd_dot = reference_velocity.y
        zd_dot = reference_velocity.theta

        y1 = pose.x + self.constant_b * math.cos(pose.theta)
        y2 = pose.y + self.constant_b * math.sin(pose.theta)

        y1d = xd + self.constant_b * math.cos(zd)
        y2d = yd + self.constant_b * math.sin(zd)

        y1d_dot = xd_dot - self.constant_b * math.sin(zd) * zd_dot
        y2d_dot = yd_dot + self.constant_b * math.cos(zd) * zd_dot

        u2 = y2d_dot + self.constant_k2 * (y2d - y2)
        u1 = y1d_dot + self.constant_k1 * (y1d - y1)

        the_v = math.cos(pose.theta) * u1 + u2 * math.sin(pose.theta)
        the_omega = (
            u1 * (-math.sin(pose.theta) / self.constant_b)
            + u2 * math.cos(pose.theta) / self.constant_b
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
