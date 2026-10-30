from abc import ABC, abstractmethod


class DifferentialDriveMovementSupervisor(ABC):
    """
    Abstract class to supervise a differential drive mobile robot in a movement

    """

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
        Method to be called when the state of the robot changes during the movement

        @type robot_state: motion.RobotState.DifferentialDriveRobotState
        @param robot_state: the new state of the robot
        """
        pass

    @abstractmethod
    def movement_end(self):
        """
        Method to be called when the movement ends

        """
        pass


class SupervisorContainer(DifferentialDriveMovementSupervisor, list):
    """
    Class that groups multiple supervisors
    """

    def __init__(self, *supervisors):
        self.extend(supervisors)

    def movement_begin(self, updates):
        for supervisor in self:
            supervisor.movement_begin(updates)

    def movement_update(self, state):
        for supervisor in self:
            supervisor.movement_update(state)

    def movement_end(self):
        for supervisor in self:
            supervisor.movement_end()
