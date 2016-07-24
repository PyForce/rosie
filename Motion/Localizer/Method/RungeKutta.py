import math
from Motion.Localizer.Differential import DifferentialDriveOdometryLocalizer

__author__ = 'Silvio'


class RungeKutta2OdometryLocalizer(DifferentialDriveOdometryLocalizer):
    """
    Class to localize a differential drive mobile robot using odometry and Runge Kutta method

    @param robot_parameters: Parameters of the robot
    @type robot_parameters: Motion.RobotParameters.DifferentialDriveRobotParameters
    """

    def __init__(self, robot_parameters):
        super(RungeKutta2OdometryLocalizer, self).__init__(robot_parameters)
        self.prev_encoder_count_1 = 0
        self.prev_encoder_count_2 = 0
        self.prev_delta_encoder_1 = 0
        self.prev_delta_encoder_2 = 0
        self.encoder_count_1 = 0
        self.encoder_count_2 = 0

    def update_location(self, delta_encoder_count_1, delta_encoder_count_2):
        """
        Update the robot's location

        @rtype : DifferentialDriveRobotLocation
        @return: Updated location
        @param delta_encoder_count_1: Count of wheel 1's encoder since last update
        @param delta_encoder_count_2: Count of wheel 2's encoder since last update
        @type delta_encoder_count_1: int
        @type delta_encoder_count_2: int
        """
        dfr = delta_encoder_count_2 * 2 * math.pi / self.robot_parameters.steps_per_revolution
        dfl = delta_encoder_count_1 * 2 * math.pi / self.robot_parameters.steps_per_revolution

        ds = (dfr + dfl) * self.robot_parameters.wheel_radius / 2
        dz = (dfr - dfl) * self.robot_parameters.wheel_radius / self.robot_parameters.wheel_distance

        self.location.x_position += ds * math.cos(self.location.z_position + dz / 2)
        self.location.y_position += ds * math.sin(self.location.z_position + dz / 2)
        self.location.z_position += dz

        self.globalLocation.x_position += ds * math.cos(self.globalLocation.z_position + dz / 2)
        self.globalLocation.y_position += ds * math.sin(self.globalLocation.z_position + dz / 2)
        self.globalLocation.z_position += dz

        return self.location, self.globalLocation
