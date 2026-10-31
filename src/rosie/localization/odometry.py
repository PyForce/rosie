import logging
import math

from rosie.models import Pose, Wheels

logger = logging.getLogger(__name__)

# s: shorter steps would divide the encoder steps by (almost) zero
MIN_ELAPSED_TIME = 0.0000000001


def advance(pose: Pose, wheels: Wheels, delta_steps_1: float, delta_steps_2: float) -> Pose:
    """
    The pose after the wheels turned these encoder steps: second-order
    Runge-Kutta, which takes the heading halfway through the step.
    """
    dfr = delta_steps_2 * 2 * math.pi / wheels.encoder_resolution
    dfl = delta_steps_1 * 2 * math.pi / wheels.encoder_resolution

    ds = (dfr + dfl) * wheels.radius / 2
    dz = (dfr - dfl) * wheels.radius / wheels.separation

    heading = pose.theta + dz / 2
    return Pose(pose.x + ds * math.cos(heading), pose.y + ds * math.sin(heading), pose.theta + dz)


def measure_speeds(
    wheels: Wheels, delta_steps_1: float, delta_steps_2: float, elapsed_time: float
) -> tuple[float, float]:
    """Both wheels' speeds (rad/s) from the encoder steps they turned in `elapsed_time`."""
    if elapsed_time < MIN_ELAPSED_TIME:
        elapsed_time = MIN_ELAPSED_TIME
        logger.warning("almost dividing by zero")
    steps_per_sec_1 = delta_steps_1 / elapsed_time
    angular_speed_1 = steps_per_sec_1 * 2 * math.pi / wheels.encoder_resolution

    steps_per_sec_2 = delta_steps_2 / elapsed_time
    angular_speed_2 = steps_per_sec_2 * 2 * math.pi / wheels.encoder_resolution

    return angular_speed_1, angular_speed_2
