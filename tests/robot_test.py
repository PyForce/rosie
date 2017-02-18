"""
Tests for the robot
"""
import unittest
from robot import Robot


class RobotTest(unittest.TestCase):
    """
    Tests for the Robot class
    """

    bot = Robot()

    def test_singleton(self):
        """
        Tests that the robot class is a singleton
        """
        new_bot = Robot()
        self.assertEqual(id(self.bot), id(new_bot))

    def test_initial_position(self):
        """
        Test that initial position is 0, 0, 0
        """
        self.assertTupleEqual(self.bot.position(), (0.0, 0.0, 0.0))
