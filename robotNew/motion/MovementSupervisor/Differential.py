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


class SupervisorContainer(DifferentialDriveMovementSupervisor, list):
    """
        Class that groups multiple supervisors
    """
    def __init__(self, *supervisors):
        self.__supervisors = [supervisor for supervisor in supervisors]

    def movement_begin(self, updates):
        for supervisor in self.__supervisors:
            supervisor.movement_begin(updates)

    def movement_update(self, state):
        for supervisor in self.__supervisors:
            supervisor.movement_update(state)

    def movement_end(self):
        for supervisor in self.__supervisors:
            supervisor.movement_end()

    # Implement list functions for supervisor operattions
    def __add__(self, *args, **kwargs):
        super(list, self.__supervisors).__add__(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        super(list, self.__supervisors).__contains__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        super(list, self.__supervisors).__getitem__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        super(list, self.__supervisors).__len__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        super(list, self.__supervisors).__setitem__(*args, **kwargs)

    def append(self, *args, **kwargs):
        super(list, self.__supervisors).append(*args, **kwargs)

    def clear(self, *args, **kwargs):
        super(list, self.__supervisors).clear(*args, **kwargs)

    def copy(self, *args, **kwargs):
        super(list, self.__supervisors).copy(*args, **kwargs)

    def count(self, *args, **kwargs):
        super(list, self.__supervisors).count(*args, **kwargs)

    def extend(self, *args, **kwargs):
        super(list, self.__supervisors).extend(*args, **kwargs)

    def index(self, *args, **kwargs):
        super(list, self.__supervisors).index(*args, **kwargs)

    def insert(self, *args, **kwargs):
        super(list, self.__supervisors).insert(*args, **kwargs)

    def pop(self, *args, **kwargs):
        super(list, self.__supervisors).pop(*args, **kwargs)

    def remove(self, *args, **kwargs):
        super(list, self.__supervisors).remove(*args, **kwargs)
