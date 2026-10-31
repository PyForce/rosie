import math

from rosie.control.models import TrackerOutput
from rosie.hardware.drive.kinematics import compute_wheel_speeds
from rosie.models import Pose, Tracking, Velocity, Wheels


def io_linearization(
    tracking: Tracking, wheels: Wheels, reference: Pose, reference_velocity: Velocity, pose: Pose
) -> TrackerOutput:
    """Input-output linearization: tracks a point at distance b ahead of the wheel axis."""
    xd = reference.x
    yd = reference.y
    zd = reference.theta

    xd_dot = reference_velocity.x
    yd_dot = reference_velocity.y
    zd_dot = reference_velocity.theta

    y1 = pose.x + tracking.b * math.cos(pose.theta)
    y2 = pose.y + tracking.b * math.sin(pose.theta)

    y1d = xd + tracking.b * math.cos(zd)
    y2d = yd + tracking.b * math.sin(zd)

    y1d_dot = xd_dot - tracking.b * math.sin(zd) * zd_dot
    y2d_dot = yd_dot + tracking.b * math.cos(zd) * zd_dot

    u2 = y2d_dot + tracking.k2 * (y2d - y2)
    u1 = y1d_dot + tracking.k1 * (y1d - y1)

    v = math.cos(pose.theta) * u1 + u2 * math.sin(pose.theta)
    omega = u1 * (-math.sin(pose.theta) / tracking.b) + u2 * math.cos(pose.theta) / tracking.b

    set_point_1, set_point_2 = compute_wheel_speeds(v, omega, wheels)
    return set_point_1, set_point_2, u1, u2
