"""Teleoperation: driving by hand, from the commands a keyboard or a joystick gives."""

from rosie.control.models import WheelSpeeds


def steer(
    steering: float, throttle: float, spin: float, command_speed: float, max_speed: float
) -> WheelSpeeds:
    """
    Racing-game driving, each command in [-1, 1]: the throttle (+1 forward) sets both
    wheels' speed, the steering (+1 right) slows one of them while moving, and the spin
    (+1 clockwise) turns on the spot when the robot isn't moving. A full command turns a
    wheel at command_speed (rad/s); max_speed is the wheels' own.
    """
    turning = steering * command_speed
    forward = throttle * command_speed
    spinning = spin * command_speed
    if (turning, forward) != (0, 0):
        wheel_1 = wheel_2 = forward
        ratio = abs(turning / max_speed)
        if turning < 0:
            wheel_1 *= 1 - ratio  # the left wheel slows: a left turn
        elif turning > 0:
            wheel_2 *= 1 - ratio
        return wheel_1, wheel_2
    if spinning:
        return spinning, -spinning
    return 0, 0
