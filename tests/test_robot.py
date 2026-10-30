"""
Tests for the robot
"""

import time
import unittest

from rosie.planning.maps import MAPS_DIR, list_maps
from rosie.profile import PROFILES_DIR, load_profile
from rosie.robot import Robot


def simubot() -> Robot:
    return Robot(
        load_profile("simubot", [PROFILES_DIR]), list_maps([MAPS_DIR]), None, time.monotonic
    )


class RobotTest(unittest.TestCase):
    """
    Tests for the Robot class
    """

    bot = simubot()

    def test_independent_robots(self) -> None:
        """
        Tests that each robot has its own state
        """
        other_bot = simubot()
        other_bot.teleport(1.0, 2.0, 0.5)
        self.assertTupleEqual(self.bot.position(), (0.0, 0.0, 0.0))

    def test_initial_position(self) -> None:
        """
        Test that initial position is 0, 0, 0
        """
        self.assertTupleEqual(self.bot.position(), (0.0, 0.0, 0.0))
