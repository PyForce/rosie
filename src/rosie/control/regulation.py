"""Regulation: bringing the robot onto a fixed point, once a planned trajectory is over."""

import math

from rosie.control.models import SetPoints
from rosie.hardware.drive.kinematics import compute_wheel_speeds
from rosie.models import Pose, Wheels

# polar go-to-point controller (1/s)
APPROACH_GAIN_DISTANCE = 1.0
APPROACH_GAIN_ANGLE = 3.0


def go_to_point(pose: Pose, target: Pose, wheels: Wheels) -> SetPoints:
    """
    Wheel speeds towards `target` once the planned trajectory is over: a polar
    go-to-point controller, which brings the wheel axis onto the point (a
    trajectory tracker can't hold a two-wheeled robot on a point).
    """
    distance = math.hypot(target.x - pose.x, target.y - pose.y)
    angle = _wrap(math.atan2(target.y - pose.y, target.x - pose.x) - pose.theta)
    direction = 1.0
    if abs(angle) > math.pi / 2:
        # the target is behind: back up instead of turning around
        angle = _wrap(angle + math.pi)
        direction = -1.0
    v = direction * APPROACH_GAIN_DISTANCE * distance * math.cos(angle)
    omega = APPROACH_GAIN_ANGLE * angle
    speed_1, speed_2 = compute_wheel_speeds(v, omega, wheels)
    return _clamp(speed_1, wheels.max_speed), _clamp(speed_2, wheels.max_speed)


def _wrap(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def _clamp(speed: float, limit: float) -> float:
    return max(-limit, min(limit, speed))
