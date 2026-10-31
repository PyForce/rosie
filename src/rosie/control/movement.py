"""
One control step of a movement, as functions: given the movement, the pose and
what the encoders just measured, the wheel speeds to ask for and the step's
Telemetry. Which controller runs (tracking, then regulation onto the last
point; or teleoperation), and when a planned movement is over.
The robot (core.py) reads the drive, calls them, and writes the drive.
"""

import logging
import math
from dataclasses import replace

from rosie.control.models import ManualMovement, PlannedMovement, Telemetry, Tracker, WheelSpeeds
from rosie.control.regulation import go_to_point
from rosie.control.teleoperation import steer
from rosie.hardware.drive.models import DriveReading
from rosie.models import STILL, Pose, RegulationSettings, TeleoperationSettings, Wheels

logger = logging.getLogger(__name__)

# s: the shortest step manual control counts
MIN_MANUAL_ELAPSED_TIME = 0.00001


def is_over(
    movement: PlannedMovement, pose: Pose, now: float, regulation: RegulationSettings
) -> bool:
    """A planned movement ends when its trajectory is done and the robot is there, or too late."""
    if not movement.trajectory_done:
        return False
    target = movement.points[-1].pose
    if math.hypot(pose.x - target.x, pose.y - target.y) <= regulation.tolerance:
        return True
    if now - movement.finished_at <= regulation.timeout:
        return False
    logger.warning(
        "stopping %.3f m short of (%.2f, %.2f): not there %.1f s after the planned time",
        math.hypot(pose.x - target.x, pose.y - target.y),
        target.x,
        target.y,
        regulation.timeout,
    )
    return True


def planned_step(
    movement: PlannedMovement,
    pose: Pose,
    speeds: tuple[float, float],
    reading: DriveReading,
    elapsed_time: float,
    now: float,
    wheels: Wheels,
    regulation: RegulationSettings,
    track: Tracker,
) -> tuple[PlannedMovement, WheelSpeeds, Telemetry]:
    """Follow the next point; once they are all followed, drive onto the last one."""
    speed_1, speed_2 = speeds
    if movement.trajectory_done:
        target = movement.points[-1].pose
        set_point_1, set_point_2 = go_to_point(pose, target, wheels, regulation.gains)
        telemetry = Telemetry(
            pose=pose,
            reference_pose=target,
            reference_velocity=STILL,
            tracker_x=None,
            tracker_y=None,
            wheel_1_speed=speed_1,
            wheel_1_setpoint=set_point_1,
            wheel_1_current=reading.current_1,
            wheel_2_speed=speed_2,
            wheel_2_setpoint=set_point_2,
            wheel_2_current=reading.current_2,
            battery_voltage=reading.battery_voltage,
            elapsed_time=elapsed_time,
        )
        return movement, (set_point_1, set_point_2), telemetry

    point = movement.points[movement.next_index]
    following = replace(movement, next_index=movement.next_index + 1)
    if following.trajectory_done:
        following = replace(following, finished_at=now)
    output = track(point.pose, point.velocity, pose)
    set_point_1, set_point_2 = output.wheel_speeds
    telemetry = Telemetry(
        pose=pose,
        reference_pose=point.pose,
        reference_velocity=point.velocity,
        tracker_x=output.x,
        tracker_y=output.y,
        wheel_1_speed=speed_1,
        wheel_1_setpoint=set_point_1,
        wheel_1_current=reading.current_1,
        wheel_2_speed=speed_2,
        wheel_2_setpoint=set_point_2,
        wheel_2_current=reading.current_2,
        battery_voltage=reading.battery_voltage,
        elapsed_time=elapsed_time,
    )
    return following, (set_point_1, set_point_2), telemetry


def manual_step(
    movement: ManualMovement,
    pose: Pose,
    speeds: tuple[float, float],
    reading: DriveReading,
    elapsed_time: float,
    wheels: Wheels,
    teleoperation: TeleoperationSettings,
) -> tuple[WheelSpeeds, Telemetry]:
    """Drive as the commands say."""
    speed_1, speed_2 = speeds
    set_point_1, set_point_2 = steer(
        movement.steering,
        movement.throttle,
        movement.spin,
        teleoperation.max_speed,
        wheels.max_speed,
    )
    telemetry = Telemetry(
        pose=pose,
        reference_pose=None,
        reference_velocity=None,
        tracker_x=None,
        tracker_y=None,
        wheel_1_speed=speed_1,
        wheel_1_setpoint=set_point_1,
        wheel_1_current=reading.current_1,
        wheel_2_speed=speed_2,
        wheel_2_setpoint=set_point_2,
        wheel_2_current=reading.current_2,
        battery_voltage=reading.battery_voltage,
        elapsed_time=elapsed_time,
    )
    return (set_point_1, set_point_2), telemetry
