from abc import ABCMeta, abstractmethod
import math
from MRobot.RobotLocation import DifferentialDriveRobotLocation
from MRobot.RobotSpeed import DifferentialDriveRobotSpeed

__author__ = 'Silvio'


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
        @type trajectory_parameters: MRobot.TrajectoryParameters.DifferentialDriveTrajectoryParameters
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


class LinearTrajectoryPlanner(DifferentialDriveTrajectoryPlanner):
    """
    Class to plan trajectories for a differential drive mobile robot using lineal interpolation

    """

    def __init__(self):
        super(LinearTrajectoryPlanner, self).__init__()
        self.reference_locations = list()
        self.reference_speeds = list()
        self.points_count = 0
        self.current_point_index = 0
        self.finished = False

    def initialize_track(self, trajectory_parameters):
        """
        Build the trajectory

        @param trajectory_parameters: Parameters of the trajectory
        @type trajectory_parameters:  MRobot.TrajectoryParameters.DifferentialDriveTrajectoryParameters
        """
        self.current_point_index = 0
        self.finished = False

        segments = len(trajectory_parameters.key_locations) - 1
        total_time = segments * trajectory_parameters.constant_t
        self.points_count = int(total_time / trajectory_parameters.sample_time)

        self.reference_locations = [DifferentialDriveRobotLocation() for i in range(self.points_count)]
        self.reference_speeds = [DifferentialDriveRobotSpeed() for i in range(self.points_count)]

        theta_prev_interval = 0
        points_per_segment = int(trajectory_parameters.constant_t / trajectory_parameters.sample_time)
        for i in range(segments):
            segment_base_index = i * points_per_segment

            delta_x = (trajectory_parameters.key_locations[i + 1].x_position -
                       trajectory_parameters.key_locations[i].x_position) / float(points_per_segment)
            delta_y = (trajectory_parameters.key_locations[i + 1].y_position -
                       trajectory_parameters.key_locations[i].y_position) / float(points_per_segment)

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

            self.reference_locations[segment_base_index].x_position = trajectory_parameters.key_locations[i].x_position
            self.reference_locations[segment_base_index].y_position = trajectory_parameters.key_locations[i].y_position
            self.reference_locations[segment_base_index].z_position = theta_interval

            self.reference_speeds[segment_base_index].x_speed = speed_x
            self.reference_speeds[segment_base_index].y_speed = speed_y
            self.reference_speeds[segment_base_index].z_speed = (theta_interval - theta_prev_interval) / float(
                trajectory_parameters.sample_time)

            theta_prev_interval = theta_interval

            for j in range(1, points_per_segment):
                self.reference_locations[segment_base_index + j].x_position = self.reference_locations[
                                                                                  segment_base_index + j - 1].x_position + delta_x
                self.reference_locations[segment_base_index + j].y_position = self.reference_locations[
                                                                                  segment_base_index + j - 1].y_position + delta_y
                self.reference_locations[segment_base_index + j].z_position = theta_interval

                self.reference_speeds[segment_base_index + j].x_speed = speed_x
                self.reference_speeds[segment_base_index + j].y_speed = speed_y
                self.reference_speeds[segment_base_index + j].z_speed = 0.

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
        @return : Tuple containing location(DifferentialDriveRobotLocation) and speed (DifferentialDriveRobotSpeed) of
        the reference robot in the current point
        """
        if self.current_point_index >= len(self.reference_locations):
            self.finished = True
            return self.reference_locations[-1], self.reference_speeds[-1]
        result = self.reference_locations[self.current_point_index], self.reference_speeds[self.current_point_index]
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


class CubicTrajectoryPlanner(DifferentialDriveTrajectoryPlanner):
    """
    Class to plan trajectories for a differential drive mobile robot using cubic interpolation

    """

    def __init__(self):
        super(CubicTrajectoryPlanner, self).__init__()
        self.reference_locations = list()
        self.reference_speeds = list()
        self.points_count = 0
        self.current_point_index = 0
        self.finished = False

    def initialize_track(self, trajectory_parameters):
        """
        Build the trajectory

        @param trajectory_parameters: Parameters of the trajectory
        @type trajectory_parameters:  MRobot.TrajectoryParameters.DifferentialDriveTrajectoryParameters
        """
        points_per_segment = int(trajectory_parameters.constant_t / float(trajectory_parameters.sample_time))

        self.current_point_index = 0
        self.finished = False

        segments = len(trajectory_parameters.key_locations) - 1

        self.points_count = points_per_segment * segments

        self.reference_locations = [DifferentialDriveRobotLocation() for i in range(self.points_count)]
        self.reference_speeds = [DifferentialDriveRobotSpeed() for i in range(self.points_count)]

        for j in range(segments):
            x_i = trajectory_parameters.key_locations[j].x_position
            y_i = trajectory_parameters.key_locations[j].y_position
            theta_i = trajectory_parameters.key_locations[j].z_position

            x_f = trajectory_parameters.key_locations[j + 1].x_position
            y_f = trajectory_parameters.key_locations[j + 1].y_position
            theta_f = trajectory_parameters.key_locations[j + 1].z_position

            alpha_x = trajectory_parameters.constant_k * math.cos(theta_f) - 3 * x_f
            alpha_y = trajectory_parameters.constant_k * math.sin(theta_f) - 3 * y_f

            beta_x = trajectory_parameters.constant_k * math.cos(theta_i) + 3 * x_i
            beta_y = trajectory_parameters.constant_k * math.sin(theta_i) + 3 * y_i

            for i in range(points_per_segment):
                s = i / float(points_per_segment)
                self.reference_locations[points_per_segment * j + i].x_position = - (s - 1) * (s - 1) * (
                    s - 1) * x_i + s * s * s * x_f + alpha_x * (
                    s * s) * (s - 1) + beta_x * s * ((s - 1) * (s - 1))
                self.reference_locations[points_per_segment * j + i].y_position = - (s - 1) * (s - 1) * (
                    s - 1) * y_i + s * s * s * y_f + alpha_y * (
                    s * s) * (s - 1) + beta_y * s * ((s - 1) * (s - 1))

                self.reference_speeds[points_per_segment * j + i].x_speed = - 3 * (s - 1) * (
                    s - 1) * x_i + 3 * s * s * x_f + alpha_x * (
                    3 * s * s - 2 * s) + beta_x * (3 * s * s - 4 * s + 1)
                self.reference_speeds[points_per_segment * j + i].y_speed = - 3 * (s - 1) * (
                    s - 1) * y_i + 3 * s * s * y_f + alpha_y * (
                    3 * s * s - 2 * s) + beta_y * (3 * s * s - 4 * s + 1)

                xd_dot_dot = - 6 * (s - 1) * x_i + 6 * s * x_f + alpha_x * (6 * s - 2) + beta_x * (6 * s - 4)
                yd_dot_dot = - 6 * (s - 1) * y_i + 6 * s * y_f + alpha_y * (6 * s - 2) + beta_y * (6 * s - 4)

                self.reference_speeds[points_per_segment * j + i].z_speed = \
                    (yd_dot_dot * self.reference_speeds[points_per_segment * j + i].x_speed - xd_dot_dot *
                     self.reference_speeds[points_per_segment * j + i].y_speed) \
                    / (self.reference_speeds[points_per_segment * j + i].x_speed * self.reference_speeds[
                        points_per_segment * j + i].x_speed
                       + self.reference_speeds[points_per_segment * j + i].y_speed * self.reference_speeds[
                           points_per_segment * j + i].y_speed)

                self.reference_speeds[points_per_segment * j + i].x_speed = \
                    self.reference_speeds[points_per_segment * j + i].x_speed / trajectory_parameters.constant_t
                self.reference_speeds[points_per_segment * j + i].y_speed = \
                    self.reference_speeds[points_per_segment * j + i].y_speed / trajectory_parameters.constant_t
                self.reference_speeds[points_per_segment * j + i].z_speed = \
                    self.reference_speeds[points_per_segment * j + i].z_speed / trajectory_parameters.constant_t

            self.reference_locations[points_per_segment * j].z_position = theta_i
            for i in range(points_per_segment - 1):
                self.reference_locations[points_per_segment * j + i + 1].z_position = \
                    self.reference_locations[points_per_segment * j + i].z_position + \
                    self.reference_speeds[points_per_segment * j + i].z_speed * trajectory_parameters.sample_time

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
        @return : Tuple containing location(DifferentialDriveRobotLocation) and speed (DifferentialDriveRobotSpeed) of
        the reference robot in the current point
        """
        if self.current_point_index >= len(self.reference_locations):
            self.finished = True
            return self.reference_locations[-1], self.reference_speeds[-1]
        result = self.reference_locations[self.current_point_index], self.reference_speeds[self.current_point_index]
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
