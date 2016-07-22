from MRobot.RobotLocation import DifferentialDriveRobotLocation
from MRobot.RobotSpeed import DifferentialDriveRobotSpeed

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
    @type reference_speed: MRobot.RobotSpeed.DifferentialDriveRobotSpeed
    @type location: MRobot.RobotLocation.DifferentialDriveRobotLocation
    @type global_location: MRobot.RobotLocation.DifferentialDriveRobotLocation
    @type reference_location: MRobot.RobotLocation.DifferentialDriveRobotLocation
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
        @type reference_speed: MRobot.RobotSpeed.DifferentialDriveRobotSpeed
        @type location: MRobot.RobotLocation.DifferentialDriveRobotLocation
        @type global_location: MRobot.RobotLocation.DifferentialDriveRobotLocation
        @type reference_location: MRobot.RobotLocation.DifferentialDriveRobotLocation
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
