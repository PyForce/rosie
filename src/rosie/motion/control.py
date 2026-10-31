"""
The control step, as functions: given the movement, the pose and what the
encoders just measured, the wheel speeds to ask for and the step's RobotState.
The robot (core.py) reads the board, calls them, and writes the board.
"""

import logging
import math
from dataclasses import replace

from rosie.motion.models import (
    STILL,
    Control,
    EncoderReading,
    Manual,
    Planned,
    Pose,
    RobotState,
    SetPoints,
    Tracker,
    Wheels,
)

logger = logging.getLogger(__name__)

# wheel speed (rad/s) for a fully pressed key under manual control
MANUAL_SPEED = 8
# polar go-to-point controller for the end of a planned movement (1/s)
APPROACH_GAIN_DISTANCE = 1.0
APPROACH_GAIN_ANGLE = 3.0
# s: shorter steps would divide the encoder steps by (almost) zero
MIN_ELAPSED_TIME = 0.0000000001
# s: the shortest step manual control counts
MIN_MANUAL_ELAPSED_TIME = 0.00001


def is_over(movement: Planned, pose: Pose, now: float, control: Control) -> bool:
    """A planned movement ends when its trajectory is done and the robot is there, or too late."""
    if not movement.trajectory_done:
        return False
    target = movement.references[-1].pose
    if math.hypot(pose.x - target.x, pose.y - target.y) <= control.arrival_tolerance:
        return True
    if now - movement.finished_at <= control.arrival_timeout:
        return False
    logger.warning(
        "stopping %.3f m short of (%.2f, %.2f): not there %.1f s after the planned time",
        math.hypot(pose.x - target.x, pose.y - target.y),
        target.x,
        target.y,
        control.arrival_timeout,
    )
    return True


def planned_step(
    movement: Planned,
    pose: Pose,
    speeds: tuple[float, float],
    reading: EncoderReading,
    elapsed_time: float,
    now: float,
    wheels: Wheels,
    track: Tracker,
) -> tuple[Planned, SetPoints, RobotState]:
    """Follow the next reference; once they are all followed, drive onto the last one."""
    _, _, battery_voltage, current_1, current_2 = reading
    speed_1, speed_2 = speeds
    if movement.trajectory_done:
        target = movement.references[-1].pose
        set_point_1, set_point_2 = approach_speeds(pose, target, wheels)
        state = RobotState(
            pose=pose,
            reference_pose=target,
            reference_velocity=STILL,
            tracker_x=None,
            tracker_y=None,
            wheel_1_speed=speed_1,
            wheel_1_setpoint=set_point_1,
            wheel_1_current=current_1,
            wheel_2_speed=speed_2,
            wheel_2_setpoint=set_point_2,
            wheel_2_current=current_2,
            battery_voltage=battery_voltage,
            elapsed_time=elapsed_time,
        )
        return movement, (set_point_1, set_point_2), state

    reference = movement.references[movement.next_index]
    following = replace(movement, next_index=movement.next_index + 1)
    if following.trajectory_done:
        following = replace(following, finished_at=now)
    set_point_1, set_point_2, u1, u2 = track(reference.pose, reference.velocity, pose)
    state = RobotState(
        pose=pose,
        reference_pose=reference.pose,
        reference_velocity=reference.velocity,
        tracker_x=u1,
        tracker_y=u2,
        wheel_1_speed=speed_1,
        wheel_1_setpoint=set_point_1,
        wheel_1_current=current_1,
        wheel_2_speed=speed_2,
        wheel_2_setpoint=set_point_2,
        wheel_2_current=current_2,
        battery_voltage=battery_voltage,
        elapsed_time=elapsed_time,
    )
    return following, (set_point_1, set_point_2), state


def manual_step(
    movement: Manual,
    pose: Pose,
    speeds: tuple[float, float],
    reading: EncoderReading,
    elapsed_time: float,
    wheels: Wheels,
) -> tuple[SetPoints, RobotState]:
    """Drive as the pressed keys say."""
    _, _, battery_voltage, current_1, current_2 = reading
    speed_1, speed_2 = speeds
    set_point_1, set_point_2 = manual_speeds(movement.keys, wheels.max_speed)
    state = RobotState(
        pose=pose,
        reference_pose=None,
        reference_velocity=None,
        tracker_x=None,
        tracker_y=None,
        wheel_1_speed=speed_1,
        wheel_1_setpoint=set_point_1,
        wheel_1_current=current_1,
        wheel_2_speed=speed_2,
        wheel_2_setpoint=set_point_2,
        wheel_2_current=current_2,
        battery_voltage=battery_voltage,
        elapsed_time=elapsed_time,
    )
    return (set_point_1, set_point_2), state


def approach_speeds(pose: Pose, target: Pose, wheels: Wheels) -> tuple[float, float]:
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
    radius = wheels.radius
    half_axis = wheels.distance / 2
    limit = wheels.max_speed
    return (
        _clamp((v - omega * half_axis) / radius, limit),
        _clamp((v + omega * half_axis) / radius, limit),
    )


def manual_speeds(keys: tuple[float, float, float], max_speed: float) -> SetPoints:
    """
    Racing-game driving from the pressed keys (each in [-1, 1]): y is the throttle,
    x steers while moving, z turns on the spot.
    """
    x, y, z = (key * MANUAL_SPEED for key in keys)
    if (x, y) != (0, 0):
        left = right = y
        ratio = abs(x / max_speed)
        if x < 0:
            right *= 1 - ratio
        elif x > 0:
            left *= 1 - ratio
        return right, left
    if z:
        return z, -z
    return 0, 0


def encoder_speeds(
    wheels: Wheels, delta_steps_1: float, delta_steps_2: float, elapsed_time: float
) -> tuple[float, float]:
    """Both wheels' speeds (rad/s) from the encoder steps they turned in `elapsed_time`."""
    if elapsed_time < MIN_ELAPSED_TIME:
        elapsed_time = MIN_ELAPSED_TIME
        logger.warning("almost dividing by zero")
    steps_per_sec_1 = delta_steps_1 / elapsed_time
    angular_speed_1 = steps_per_sec_1 * 2 * math.pi / wheels.encoder_steps

    steps_per_sec_2 = delta_steps_2 / elapsed_time
    angular_speed_2 = steps_per_sec_2 * 2 * math.pi / wheels.encoder_steps

    return angular_speed_1, angular_speed_2


def _wrap(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def _clamp(speed: float, limit: float) -> float:
    return max(-limit, min(limit, speed))
