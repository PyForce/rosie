"""
A client for rosie's web API, for scripts and notebooks:

    from rosie.client import RosieClient

    robot = RosieClient("http://localhost:5000")
    robot.goto(1, 0.5, 4)
    for position in robot.positions():
        if position.distance_to(1, 0.5) < 0.01:
            break
"""

from rosie.client.api import RosieClient
from rosie.client.models import Position, RobotInfo

__all__ = ["Position", "RobotInfo", "RosieClient"]
