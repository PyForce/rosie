from abc import ABCMeta, abstractmethod


__author__ = 'Silvio'


class DifferentialDriveTrajectoryParameters:
    """
    Structure containing data to generate trajectories

    @param constant_t: Time between key points
    @type constant_t: float
    @param constant_k: Constant for cubic interpolations
    @type constant_k: float
    @param sample_time: Sample time between two interpolated points
    @type sample_time: float
    @param key_locations: Tuple (n DifferentialDriveRobotLocation) containing all points to generate path by interpolation
    @type key_locations: tuple
    """

    def __init__(self, key_locations, constant_t, sample_time, constant_k=0.):
        self.constant_t = constant_t
        self.constant_k = constant_k
        self.sample_time = sample_time
        self.key_locations = key_locations


class DifferentialDriveTrajectoryPlanner:
    """
    Abstract class to plan trajectories for a differential drive mobile robot

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def initialize_track(self, trajectory_parameters):
        """
        Build the trajectory

        @param trajectory_parameters: Parameters of the trajectory
        @type trajectory_parameters: motion.TrajectoryParameters.DifferentialDriveTrajectoryParameters
        """
        pass

    @abstractmethod
    def has_finished(self):
        """
        Return if the trajectory has finished

        @rtype : bool
        @return: True if the trajectory has finished, False otherwise
        """
        pass

    @abstractmethod
    def get_next_point(self):
        """
        Get the location and speed for the next point in the trajectory

        @rtype : tuple
        @return : Tuple containing location(DifferentialDriveRobotLocation) and speed (DifferentialDriveRobotSpeed) of
        the reference robot in the current point
        """
        pass

    @abstractmethod
    def get_length(self):
        """
        Get the number of points in the trajectory

        @return: The length of the trajectory (number of points)
        @rtype: int
        """
        pass
