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
