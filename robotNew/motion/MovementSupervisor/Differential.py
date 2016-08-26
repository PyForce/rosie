from abc import ABCMeta, abstractmethod
import thread

__author__ = 'Silvio'


class DifferentialDriveMovementSupervisor:
    """
    Abstract class to supervise a differential drive mobile robotNew in a movement
    
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def movement_begin(self, expected_updates):
        """
        Method to be called when the movement begins

        @param expected_updates: Number of times movement_updates wil be called
        @type expected_updates: int
        """
        pass

    @abstractmethod
    def movement_update(self, robot_state):
        """
        Method to be called when the state of the robotNew changes during the movement
        
        @type robot_state: motion.RobotState.DifferentialDriveRobotState
        @param robot_state: the new state of the robotNew
        """
        pass

    @abstractmethod
    def movement_end(self):
        """
        Method to be called when the movement ends

        """
        pass


