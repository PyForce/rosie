class HardwareUnavailableError(RuntimeError):
    """A profile needs hardware (or its library) that this machine doesn't have."""


class NoRouteError(ValueError):
    """The planner can't take the robot there (no map, or the target is out of reach)."""
