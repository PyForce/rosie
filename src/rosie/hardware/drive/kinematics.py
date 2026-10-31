"""The differential drive's kinematic model, from the profile's [wheels]."""

from rosie.models import Wheels


def compute_wheel_speeds(v: float, omega: float, wheels: Wheels) -> tuple[float, float]:
    """
    The two wheel speeds (rad/s) that move the robot forward at v (m/s) while it
    turns at omega (rad/s, counter-clockwise): (v - ω d/2) / r and (v + ω d/2) / r.
    """
    half_axis = wheels.separation / 2
    return (v - omega * half_axis) / wheels.radius, (v + omega * half_axis) / wheels.radius
