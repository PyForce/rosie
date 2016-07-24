import math
from Motion.MovementController.Differential import DifferentialDriveRobotLocation, DifferentialDriveRobotSpeed
from Motion.TrajectoryPlanner.Differential import DifferentialDriveTrajectoryPlanner

__author__ = 'Silvio'


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
        @type trajectory_parameters:  Motion.TrajectoryParameters.DifferentialDriveTrajectoryParameters
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
