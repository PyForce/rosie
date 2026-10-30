class HardwareUnavailableError(RuntimeError):
    """A profile needs hardware (or its library) that this machine doesn't have."""


class NoRouteError(ValueError):
    """The planner can't take the robot there (no map, or the target is out of reach)."""


class RequestError(RuntimeError):
    """rosie refused a request (the client's view of an HTTP error)."""

    def __init__(self, status: int, detail: str) -> None:
        super().__init__(f"{status}: {detail}")
        self.status = status
        self.detail = detail
