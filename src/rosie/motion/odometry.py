import math
from abc import ABC, abstractmethod

from rosie.motion.models import ORIGIN, Pose, Wheels


class OdometryLocalizer(ABC):
    def __init__(self, wheels: Wheels) -> None:
        self.wheels = wheels
        self.pose = ORIGIN

    @abstractmethod
    def update_location(self, delta_steps_1: float, delta_steps_2: float) -> Pose:
        """The pose after the wheels turned these encoder steps."""


class RungeKutta2Localizer(OdometryLocalizer):
    def update_location(self, delta_steps_1: float, delta_steps_2: float) -> Pose:
        dfr = delta_steps_2 * 2 * math.pi / self.wheels.encoder_steps
        dfl = delta_steps_1 * 2 * math.pi / self.wheels.encoder_steps

        ds = (dfr + dfl) * self.wheels.radius / 2
        dz = (dfr - dfl) * self.wheels.radius / self.wheels.distance

        self.pose = _advance(self.pose, ds, dz)
        return self.pose


def _advance(pose: Pose, ds: float, dz: float) -> Pose:
    heading = pose.theta + dz / 2
    return Pose(pose.x + ds * math.cos(heading), pose.y + ds * math.sin(heading), pose.theta + dz)
