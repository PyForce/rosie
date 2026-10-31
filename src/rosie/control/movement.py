"""
One control step of a movement, as functions: given the movement, the pose and
what the encoders just measured, the wheel speeds to ask for and the step's
RobotState. Which controller runs (tracking, then regulation onto the last
point; or teleoperation), and when a planned movement is over.
The robot (core.py) reads the drive, calls them, and writes the drive.
"""

import logging
import math
from dataclasses import replace

from rosie.control.models import ManualMovement, PlannedMovement, RobotState, Tracker, WheelSpeeds
from rosie.control.regulation import go_to_point
from rosie.control.teleoperation import steer
from rosie.hardware.drive.models import EncoderReading
from rosie.models import STILL, ControlSettings, Pose, Wheels

logger = logging.getLogger(__name__)

# s: the shortest step manual control counts
MIN_MANUAL_ELAPSED_TIME = 0.00001


def is_over(movement: PlannedMovement, pose: Pose, now: float, control: ControlSettings) -> bool:
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
    movement: PlannedMovement,
    pose: Pose,
    speeds: tuple[float, float],
    reading: EncoderReading,
    elapsed_time: float,
    now: float,
    wheels: Wheels,
    track: Tracker,
) -> tuple[PlannedMovement, WheelSpeeds, RobotState]:
    """Follow the next reference; once they are all followed, drive onto the last one."""
    _, _, battery_voltage, current_1, current_2 = reading
    speed_1, speed_2 = speeds
    if movement.trajectory_done:
        target = movement.references[-1].pose
        set_point_1, set_point_2 = go_to_point(pose, target, wheels)
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
    movement: ManualMovement,
    pose: Pose,
    speeds: tuple[float, float],
    reading: EncoderReading,
    elapsed_time: float,
    wheels: Wheels,
) -> tuple[WheelSpeeds, RobotState]:
    """Drive as the commands say."""
    _, _, battery_voltage, current_1, current_2 = reading
    speed_1, speed_2 = speeds
    set_point_1, set_point_2 = steer(
        movement.steering, movement.throttle, movement.spin, wheels.max_speed
    )
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
