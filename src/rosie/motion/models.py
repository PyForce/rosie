"""
Locations, speeds, state and parameters of a differential drive robot
"""


class Pose:
    """
    Structure containing the cartesian coordinates of a robot

    @param x: Position on the X axis
    @param y: Position on the Y axis
    @param theta: Position on the Z axis (angle, pose)
    """

    def __init__(self, x=0.0, y=0.0, theta=0.0):
        self.theta = theta
        self.y = y
        self.x = x

    def reset(self):
        """
        Reset the location to the origin

        """
        self.theta = 0.0
        self.y = 0.0
        self.x = 0.0

    def __repr__(self):
        return "(%f,%f,%f)" % (self.x, self.y, self.theta)


class RobotParameters:
    """
    Structure containing parameters for a differential drive mobile robot

    @param wheel_radius: Radius of the wheels
    @param wheel_distance: Distance between wheels
    @param steps_per_revolution: Encoders counts for a complete revolution of the wheels
    @param constant_b: Distance of the P point when using IOLinearization Controller
    @param constant_k1: Gain for X axis when using IO Linearization Controller
    @param constant_k2: Gain for Y axis when using IO Linearization Controller
    @param constant_ki: Integrative gain using PID Controller for the speeds
    @param constant_kd: Derivative gain using PID Controller for the speeds
    @param constant_kc: Proportional gain using PID Controller for the speeds
    @param max_value_power: Maximum value of the power to be driven to motors
    @param min_value_power: Minimum value of the power to be driven to motors
    @param sample_time: Sample time for the control system

    @type constant_kc: float
    @type constant_kd: float
    @type constant_ki: float
    @type constant_k2: float
    @type constant_k1: float
    @type constant_b: float
    @type steps_per_revolution: float
    @type wheel_distance: float
    @type wheel_radius: float
    @type max_value_power: float
    @type min_value_power: float
    @type sample_time: float
    """

    def __init__(
        self,
        wheel_radius,
        wheel_distance,
        steps_per_revolution,
        constant_b,
        constant_k1,
        constant_k2,
        constant_ki,
        constant_kd,
        constant_kc,
        max_value_power,
        min_value_power,
        sample_time,
        max_speed,
    ):
        self.sample_time = sample_time
        self.max_value_power = max_value_power
        self.min_value_power = min_value_power
        self.constant_kc = constant_kc
        self.constant_kd = constant_kd
        self.constant_ki = constant_ki
        self.constant_k2 = constant_k2
        self.constant_k1 = constant_k1
        self.constant_b = constant_b
        self.steps_per_revolution = steps_per_revolution
        self.wheel_distance = wheel_distance
        self.wheel_radius = wheel_radius
        self.max_speed = max_speed


class Velocity:
    """
    Structure containing speeds of a robot

    @param x: Component of the speed on the X axis
    @type x: float
    @param y: Component of the speed on the Y axis
    @type x: float
    @param theta: Component of the speed on the Z axis (angular speed)
    @type x: float
    """

    def __init__(self, x=0.0, y=0.0, theta=0.0):
        self.theta = theta
        self.y = y
        self.x = x

    def __repr__(self):
        return "(%f,%f,%f)" % (self.x, self.y, self.theta)


class RobotState:
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
    @type reference_speed: motion.RobotSpeed.Velocity
    @type location: motion.RobotLocation.Pose
    @type global_location: motion.RobotLocation.Pose
    @type reference_location: motion.RobotLocation.Pose
    """

    def __init__(
        self,
        location=Pose(),
        global_location=Pose(),
        reference_location=Pose(),
        reference_speed=Velocity,
        x_speed_ref=0.0,
        y_speed_ref=0.0,
        angular_speed_1=0.0,
        set_point_1=0.0,
        current_1=0.0,
        angular_speed_2=0.0,
        set_point_2=0.0,
        current_2=0.0,
        battery_voltage=0.0,
        elapsed_time=0.0,
    ):
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

    def update(
        self,
        location,
        global_location,
        reference_location,
        reference_speed,
        x_speed_ref,
        y_speed_ref,
        angular_speed_1,
        set_point_1,
        current_1,
        angular_speed_2,
        set_point_2,
        current_2,
        battery_voltage,
        elapsed_time,
    ):
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
        @type reference_speed: motion.RobotSpeed.Velocity
        @type location: motion.RobotLocation.Pose
        @type global_location: motion.RobotLocation.Pose
        @type reference_location: motion.RobotLocation.Pose
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
