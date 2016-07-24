from abc import ABCMeta, abstractmethod
from Motion.MovementController.Differential import DifferentialDriveRobotLocation, DifferentialDriveRobotSpeed

__author__ = 'Silvio'


class DifferentialDriveRobotState:
    """
    Class to represent the state of a differential drive mobile robot

    @param elapsed_time: elapsed time since last state update
    @param battery_voltage: voltage of the battery of the robot
    @param current_2: current of the motor 2
    @param set_point_2: speed of reference of the motor 2
    @param angular_speed_2: speed of the motor 2
    @param current_1: current of the motor 1
    @param set_point_1: speed of reference of the motor 1
    @param angular_speed_1: speed of the motor 1
    @param y_speed_ref: corrected speed of reference in X axis
    @param x_speed_ref: corrected speed of reference in Y axis
    @param reference_speed: speed of reference of the robot
    @param location: location of the robot
    @param global_location: location of the robot (global)
    @param reference_location: location of reference of the robot

    @type elapsed_time: float
    @type battery_voltage: float
    @type current_2: float
    @type set_point_2: float
    @type angular_speed_2: float
    @type current_1: float
    @type set_point_1: float
    @type angular_speed_1: float
    @type y_speed_ref: float
    @type x_speed_ref: float
    @type reference_speed: Motion.RobotSpeed.DifferentialDriveRobotSpeed
    @type location: Motion.RobotLocation.DifferentialDriveRobotLocation
    @type global_location: Motion.RobotLocation.DifferentialDriveRobotLocation
    @type reference_location: Motion.RobotLocation.DifferentialDriveRobotLocation
    """

    def __init__(self, location=DifferentialDriveRobotLocation(), global_location=DifferentialDriveRobotLocation(),
                 reference_location=DifferentialDriveRobotLocation(), reference_speed=DifferentialDriveRobotSpeed,
                 x_speed_ref=0., y_speed_ref=0., angular_speed_1=0., set_point_1=0., current_1=0., angular_speed_2=0.,
                 set_point_2=0., current_2=0., battery_voltage=0., elapsed_time=0.):
        self.global_location = global_location
        self.elapsed_time = elapsed_time
        self.battery_voltage = battery_voltage
        self.current_2 = current_2
        self.set_point_2 = set_point_2
        self.angular_speed_2 = angular_speed_2
        self.current_1 = current_1
        self.set_point_1 = set_point_1
        self.angular_speed_1 = angular_speed_1
        self.y_speed_ref = y_speed_ref
        self.x_speed_ref = x_speed_ref
        self.reference_speed = reference_speed
        self.reference_location = reference_location
        self.location = location

    def update(self, location, global_location, reference_location, reference_speed, x_speed_ref, y_speed_ref,
               angular_speed_1,
               set_point_1, current_1, angular_speed_2, set_point_2, current_2, battery_voltage, elapsed_time):
        """
        Method to update the state of the robot

        @param elapsed_time: elapsed time since last state update
        @param battery_voltage: voltage of the battery of the robot
        @param current_2: current of the motor 2
        @param set_point_2: speed of reference of the motor 2
        @param angular_speed_2: speed of the motor 2
        @param current_1: current of the motor 1
        @param set_point_1: speed of reference of the motor 1
        @param angular_speed_1: speed of the motor 1
        @param y_speed_ref: corrected speed of reference in X axis
        @param x_speed_ref: corrected speed of reference in Y axis
        @param reference_speed: speed of reference of the robot
        @param location: location of the robot
        @param global_location: location of the robot (global)
        @param reference_location: location of reference of the robot

        @type elapsed_time: float
        @type battery_voltage: float
        @type current_2: float
        @type set_point_2: float
        @type angular_speed_2: float
        @type current_1: float
        @type set_point_1: float
        @type angular_speed_1: float
        @type y_speed_ref: float
        @type x_speed_ref: float
        @type reference_speed: Motion.RobotSpeed.DifferentialDriveRobotSpeed
        @type location: Motion.RobotLocation.DifferentialDriveRobotLocation
        @type global_location: Motion.RobotLocation.DifferentialDriveRobotLocation
        @type reference_location: Motion.RobotLocation.DifferentialDriveRobotLocation
        """
        self.global_location = global_location
        self.elapsed_time = elapsed_time
        self.battery_voltage = battery_voltage
        self.current_2 = current_2
        self.set_point_2 = set_point_2
        self.angular_speed_2 = angular_speed_2
        self.current_1 = current_1
        self.set_point_1 = set_point_1
        self.angular_speed_1 = angular_speed_1
        self.y_speed_ref = y_speed_ref
        self.x_speed_ref = x_speed_ref
        self.reference_speed = reference_speed
        self.reference_location = reference_location
        self.location = location


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
        @type trajectory_parameters: Motion.TrajectoryParameters.DifferentialDriveTrajectoryParameters
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
