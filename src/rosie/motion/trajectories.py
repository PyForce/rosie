import math
from abc import ABC, abstractmethod

from rosie.motion.models import Pose, Velocity


class TrajectoryParameters:
    """
    Structure containing data to generate trajectories

    @param constant_t: Time between key points
    @type constant_t: float
    @param constant_k: Constant for cubic interpolations
    @type constant_k: float
    @param sample_time: Sample time between two interpolated points
    @type sample_time: float
    @param key_locations: Tuple (n Pose) containing all points to generate path by interpolation
    @type key_locations: tuple
    """

    def __init__(self, key_locations, constant_t, sample_time, constant_k=0.0):
        self.constant_t = constant_t
        self.constant_k = constant_k
        self.sample_time = sample_time
        self.key_locations = key_locations


class TrajectoryPlanner(ABC):
    """
    Abstract class to plan trajectories for a differential drive mobile robot

    """

    def __init__(self):
        pass

    @abstractmethod
    def initialize_track(self, trajectory_parameters):
        """
        Build the trajectory

        @param trajectory_parameters: Parameters of the trajectory
        @type trajectory_parameters: motion.TrajectoryParameters.TrajectoryParameters
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
        @return : Tuple containing location(Pose) and speed (Velocity) of
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


class LinearTrajectoryPlanner(TrajectoryPlanner):
    """
    Class to plan trajectories for a differential drive mobile robot using lineal interpolation

    """

    def __init__(self):
        super().__init__()
        self.reference_locations = list()
        self.reference_speeds = list()
        self.points_count = 0
        self.current_point_index = 0
        self.finished = False

    def initialize_track(self, trajectory_parameters):
        """
        Build the trajectory

        @param trajectory_parameters: Parameters of the trajectory
        @type trajectory_parameters:  motion.TrajectoryParameters.TrajectoryParameters
        """
        self.current_point_index = 0
        self.finished = False

        segments = len(trajectory_parameters.key_locations) - 1
        total_time = segments * trajectory_parameters.constant_t
        self.points_count = int(total_time / trajectory_parameters.sample_time)

        self.reference_locations = [
            Pose() for i in range(self.points_count)
        ]
        self.reference_speeds = [Velocity() for i in range(self.points_count)]

        theta_prev_interval = 0
        points_per_segment = int(
            trajectory_parameters.constant_t / trajectory_parameters.sample_time
        )
        for i in range(segments):
            segment_base_index = i * points_per_segment

            delta_x = (
                trajectory_parameters.key_locations[i + 1].x
                - trajectory_parameters.key_locations[i].x
            ) / float(points_per_segment)
            delta_y = (
                trajectory_parameters.key_locations[i + 1].y
                - trajectory_parameters.key_locations[i].y
            ) / float(points_per_segment)

            speed_x = delta_x / trajectory_parameters.sample_time
            speed_y = delta_y / trajectory_parameters.sample_time

            theta_interval = math.atan2(speed_y, speed_x)

            diff1 = abs(theta_interval - theta_prev_interval)
            diff2 = abs(theta_interval + 2 * math.pi - theta_prev_interval)
            diff3 = abs(theta_interval - 2 * math.pi - theta_prev_interval)

            if diff2 < diff1:
                if diff2 < diff3:
                    theta_interval += 2 * math.pi
                else:
                    theta_interval -= 2 * math.pi
            else:
                if diff3 < diff1:
                    theta_interval += 2 * math.pi

            self.reference_locations[
                segment_base_index
            ].x = trajectory_parameters.key_locations[i].x
            self.reference_locations[
                segment_base_index
            ].y = trajectory_parameters.key_locations[i].y
            self.reference_locations[segment_base_index].theta = theta_interval

            self.reference_speeds[segment_base_index].x = speed_x
            self.reference_speeds[segment_base_index].y = speed_y
            self.reference_speeds[segment_base_index].theta = (
                theta_interval - theta_prev_interval
            ) / float(trajectory_parameters.sample_time)

            theta_prev_interval = theta_interval

            for j in range(1, points_per_segment):
                self.reference_locations[segment_base_index + j].x = (
                    self.reference_locations[segment_base_index + j - 1].x + delta_x
                )
                self.reference_locations[segment_base_index + j].y = (
                    self.reference_locations[segment_base_index + j - 1].y + delta_y
                )
                self.reference_locations[segment_base_index + j].theta = theta_interval

                self.reference_speeds[segment_base_index + j].x = speed_x
                self.reference_speeds[segment_base_index + j].y = speed_y
                self.reference_speeds[segment_base_index + j].theta = 0.0

    def get_length(self):
        """
        Get the number of points in the trajectory

        @return: The length of the trajectory (number of points)
        @rtype: int
        """
        return self.points_count

    def get_next_point(self):
        """
        Get the location and speed for the next point in the trajectory

        @rtype : tuple
        @return : Tuple containing location(Pose) and speed (Velocity) of
        the reference robot in the current point
        """
        if self.current_point_index >= len(self.reference_locations):
            self.finished = True
            return self.reference_locations[-1], self.reference_speeds[-1]
        result = (
            self.reference_locations[self.current_point_index],
            self.reference_speeds[self.current_point_index],
        )
        self.current_point_index += 1
        if self.current_point_index >= len(self.reference_locations):
            self.finished = True
        return result

    def has_finished(self):
        """
        Return if the trajectory has finished

        @rtype : bool
        @return: True if the trajectory has finished, False otherwise
        """
        return self.finished


class CubicTrajectoryPlanner(TrajectoryPlanner):
    """
    Class to plan trajectories for a differential drive mobile robot using cubic interpolation

    """

    def __init__(self):
        super().__init__()
        self.reference_locations = list()
        self.reference_speeds = list()
        self.points_count = 0
        self.current_point_index = 0
        self.finished = False

    def initialize_track(self, trajectory_parameters):
        """
        Build the trajectory

        @param trajectory_parameters: Parameters of the trajectory
        @type trajectory_parameters:  motion.TrajectoryParameters.TrajectoryParameters
        """
        points_per_segment = int(
            trajectory_parameters.constant_t / float(trajectory_parameters.sample_time)
        )

        self.current_point_index = 0
        self.finished = False

        segments = len(trajectory_parameters.key_locations) - 1

        self.points_count = points_per_segment * segments

        self.reference_locations = [
            Pose() for i in range(self.points_count)
        ]
        self.reference_speeds = [Velocity() for i in range(self.points_count)]

        for j in range(segments):
            x_i = trajectory_parameters.key_locations[j].x
            y_i = trajectory_parameters.key_locations[j].y
            theta_i = trajectory_parameters.key_locations[j].theta

            x_f = trajectory_parameters.key_locations[j + 1].x
            y_f = trajectory_parameters.key_locations[j + 1].y
            theta_f = trajectory_parameters.key_locations[j + 1].theta

            alpha_x = trajectory_parameters.constant_k * math.cos(theta_f) - 3 * x_f
            alpha_y = trajectory_parameters.constant_k * math.sin(theta_f) - 3 * y_f

            beta_x = trajectory_parameters.constant_k * math.cos(theta_i) + 3 * x_i
            beta_y = trajectory_parameters.constant_k * math.sin(theta_i) + 3 * y_i

            for i in range(points_per_segment):
                s = i / float(points_per_segment)
                self.reference_locations[points_per_segment * j + i].x = (
                    -(s - 1) * (s - 1) * (s - 1) * x_i
                    + s * s * s * x_f
                    + alpha_x * (s * s) * (s - 1)
                    + beta_x * s * ((s - 1) * (s - 1))
                )
                self.reference_locations[points_per_segment * j + i].y = (
                    -(s - 1) * (s - 1) * (s - 1) * y_i
                    + s * s * s * y_f
                    + alpha_y * (s * s) * (s - 1)
                    + beta_y * s * ((s - 1) * (s - 1))
                )

                self.reference_speeds[points_per_segment * j + i].x = (
                    -3 * (s - 1) * (s - 1) * x_i
                    + 3 * s * s * x_f
                    + alpha_x * (3 * s * s - 2 * s)
                    + beta_x * (3 * s * s - 4 * s + 1)
                )
                self.reference_speeds[points_per_segment * j + i].y = (
                    -3 * (s - 1) * (s - 1) * y_i
                    + 3 * s * s * y_f
                    + alpha_y * (3 * s * s - 2 * s)
                    + beta_y * (3 * s * s - 4 * s + 1)
                )

                xd_dot_dot = (
                    -6 * (s - 1) * x_i + 6 * s * x_f + alpha_x * (6 * s - 2) + beta_x * (6 * s - 4)
                )
                yd_dot_dot = (
                    -6 * (s - 1) * y_i + 6 * s * y_f + alpha_y * (6 * s - 2) + beta_y * (6 * s - 4)
                )

                self.reference_speeds[points_per_segment * j + i].theta = (
                    yd_dot_dot * self.reference_speeds[points_per_segment * j + i].x
                    - xd_dot_dot * self.reference_speeds[points_per_segment * j + i].y
                ) / (
                    self.reference_speeds[points_per_segment * j + i].x
                    * self.reference_speeds[points_per_segment * j + i].x
                    + self.reference_speeds[points_per_segment * j + i].y
                    * self.reference_speeds[points_per_segment * j + i].y
                )

                self.reference_speeds[points_per_segment * j + i].x = (
                    self.reference_speeds[points_per_segment * j + i].x
                    / trajectory_parameters.constant_t
                )
                self.reference_speeds[points_per_segment * j + i].y = (
                    self.reference_speeds[points_per_segment * j + i].y
                    / trajectory_parameters.constant_t
                )
                self.reference_speeds[points_per_segment * j + i].theta = (
                    self.reference_speeds[points_per_segment * j + i].theta
                    / trajectory_parameters.constant_t
                )

            self.reference_locations[points_per_segment * j].theta = theta_i
            for i in range(points_per_segment - 1):
                self.reference_locations[points_per_segment * j + i + 1].theta = (
                    self.reference_locations[points_per_segment * j + i].theta
                    + self.reference_speeds[points_per_segment * j + i].theta
                    * trajectory_parameters.sample_time
                )

    def get_length(self):
        """
        Get the number of points in the trajectory

        @return: The length of the trajectory (number of points)
        @rtype: int
        """
        return self.points_count

    def get_next_point(self):
        """
        Get the location and speed for the next point in the trajectory

        @rtype : tuple
        @return : Tuple containing location(Pose) and speed (Velocity) of
        the reference robot in the current point
        """
        if self.current_point_index >= len(self.reference_locations):
            self.finished = True
            return self.reference_locations[-1], self.reference_speeds[-1]
        result = (
            self.reference_locations[self.current_point_index],
            self.reference_speeds[self.current_point_index],
        )
        self.current_point_index += 1
        if self.current_point_index >= len(self.reference_locations):
            self.finished = True
        return result

    def has_finished(self):
        """
        Return if the trajectory has finished

        @rtype : bool
        @return: True if the trajectory has finished, False otherwise
        """
        return self.finished
