"""
Tests for the robot
"""

import time
import unittest

from rosie.robot import Robot


class RobotTest(unittest.TestCase):
    """
    Tests for the Robot class
    """

    bot = Robot("simubot", None, time.monotonic)

    def test_independent_robots(self):
        """
        Tests that each robot has its own state
        """
        other_bot = Robot("simubot", None, time.monotonic)
        other_bot.teleport(1.0, 2.0, 0.5)
        self.assertTupleEqual(self.bot.position(), (0.0, 0.0, 0.0))

    def test_initial_position(self):
        """
        Test that initial position is 0, 0, 0
        """
        self.assertTupleEqual(self.bot.position(), (0.0, 0.0, 0.0))
