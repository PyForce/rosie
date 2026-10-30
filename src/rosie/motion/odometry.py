import math
from abc import ABC, abstractmethod

from rosie.motion.models import ORIGIN, Pose, RobotParameters


class OdometryLocalizer(ABC):
    def __init__(self, robot_parameters: RobotParameters) -> None:
        self.robot_parameters = robot_parameters
        self.location = ORIGIN
        self.global_location = ORIGIN

    @abstractmethod
    def update_location(self, delta_steps_1: float, delta_steps_2: float) -> tuple[Pose, Pose]:
        """New (location, global location) after the wheels turned these encoder steps."""


class RungeKutta2Localizer(OdometryLocalizer):
    def update_location(self, delta_steps_1: float, delta_steps_2: float) -> tuple[Pose, Pose]:
        dfr = delta_steps_2 * 2 * math.pi / self.robot_parameters.steps_per_revolution
        dfl = delta_steps_1 * 2 * math.pi / self.robot_parameters.steps_per_revolution

        ds = (dfr + dfl) * self.robot_parameters.wheel_radius / 2
        dz = (dfr - dfl) * self.robot_parameters.wheel_radius / self.robot_parameters.wheel_distance

        self.location = _advance(self.location, ds, dz)
        self.global_location = _advance(self.global_location, ds, dz)
        return self.location, self.global_location


def _advance(pose: Pose, ds: float, dz: float) -> Pose:
    heading = pose.theta + dz / 2
    return Pose(pose.x + ds * math.cos(heading), pose.y + ds * math.sin(heading), pose.theta + dz)
