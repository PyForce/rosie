import math

from rosie.motion.models import Pose, Wheels


def advance(pose: Pose, wheels: Wheels, delta_steps_1: float, delta_steps_2: float) -> Pose:
    """
    The pose after the wheels turned these encoder steps: second-order
    Runge-Kutta, which takes the heading halfway through the step.
    """
    dfr = delta_steps_2 * 2 * math.pi / wheels.encoder_steps
    dfl = delta_steps_1 * 2 * math.pi / wheels.encoder_steps

    ds = (dfr + dfl) * wheels.radius / 2
    dz = (dfr - dfl) * wheels.radius / wheels.distance

    heading = pose.theta + dz / 2
    return Pose(pose.x + ds * math.cos(heading), pose.y + ds * math.sin(heading), pose.theta + dz)
