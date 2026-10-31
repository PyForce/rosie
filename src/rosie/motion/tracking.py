import math
from abc import ABC, abstractmethod

from rosie.motion.models import Pose, TrackerOutput, Tracking, Velocity, Wheels


class TrajectoryTracker(ABC):
    @abstractmethod
    def track(self, reference: Pose, reference_velocity: Velocity, pose: Pose) -> TrackerOutput: ...

    @abstractmethod
    def reset(self) -> None: ...


class IOLinearizationTracker(TrajectoryTracker):
    """Input-output linearization: tracks a point at distance b ahead of the wheel axis."""

    def __init__(self, tracking: Tracking, wheels: Wheels) -> None:
        self.wheels = wheels
        self.k2 = tracking.k2
        self.k1 = tracking.k1
        self.b = tracking.b

    def reset(self) -> None:
        pass

    def track(self, reference: Pose, reference_velocity: Velocity, pose: Pose) -> TrackerOutput:
        xd = reference.x
        yd = reference.y
        zd = reference.theta

        xd_dot = reference_velocity.x
        yd_dot = reference_velocity.y
        zd_dot = reference_velocity.theta

        y1 = pose.x + self.b * math.cos(pose.theta)
        y2 = pose.y + self.b * math.sin(pose.theta)

        y1d = xd + self.b * math.cos(zd)
        y2d = yd + self.b * math.sin(zd)

        y1d_dot = xd_dot - self.b * math.sin(zd) * zd_dot
        y2d_dot = yd_dot + self.b * math.cos(zd) * zd_dot

        u2 = y2d_dot + self.k2 * (y2d - y2)
        u1 = y1d_dot + self.k1 * (y1d - y1)

        v = math.cos(pose.theta) * u1 + u2 * math.sin(pose.theta)
        omega = u1 * (-math.sin(pose.theta) / self.b) + u2 * math.cos(pose.theta) / self.b

        set_point_2 = v / self.wheels.radius + omega * self.wheels.distance / 2 / self.wheels.radius
        set_point_1 = v / self.wheels.radius - omega * self.wheels.distance / 2 / self.wheels.radius

        return set_point_1, set_point_2, u1, u2
