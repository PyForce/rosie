"""Teleoperation: driving by hand, from the pressed keys."""

from rosie.control.models import SetPoints

# wheel speed (rad/s) for a fully pressed key
MANUAL_SPEED = 8


def from_keys(keys: tuple[float, float, float], max_speed: float) -> SetPoints:
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
