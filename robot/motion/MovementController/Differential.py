import math
import time
import logging

class DifferentialDriveRobotLocation:
    """
    Structure containing the cartesian coordinates of a robot

    @param x_position: Position on the X axis
    @param y_position: Position on the Y axis
    @param z_position: Position on the Z axis (angle, pose)
    """

    def __init__(self, x_position=0., y_position=0., z_position=0.):
        self.z_position = z_position
        self.y_position = y_position
        self.x_position = x_position

    def reset(self):
        """
        Reset the location to the origin

        """
        self.z_position = 0.
        self.y_position = 0.
        self.x_position = 0.

    def __repr__(self):
        return "(%f,%f,%f)" % (self.x_position, self.y_position, self.z_position)


class DifferentialDriveRobotParameters:
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

    def __init__(self, wheel_radius, wheel_distance, steps_per_revolution, constant_b, constant_k1, constant_k2,
                 constant_ki, constant_kd, constant_kc, max_value_power, min_value_power, sample_time,max_speed):
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
        self.max_speed=max_speed


class DifferentialDriveRobotSpeed:
    """
    Structure containing speeds of a robot

    @param x_speed: Component of the speed on the X axis
    @type x_speed: float
    @param y_speed: Component of the speed on the Y axis
    @type x_speed: float
    @param z_speed: Component of the speed on the Z axis (angular speed)
    @type x_speed: float
    """

    def __init__(self, x_speed=0., y_speed=0., z_speed=0.):
        self.z_speed = z_speed
        self.y_speed = y_speed
        self.x_speed = x_speed

    def __repr__(self):
        return "(%f,%f,%f)" % (self.x_speed, self.y_speed, self.z_speed)



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
    @type reference_speed: motion.RobotSpeed.DifferentialDriveRobotSpeed
    @type location: motion.RobotLocation.DifferentialDriveRobotLocation
    @type global_location: motion.RobotLocation.DifferentialDriveRobotLocation
    @type reference_location: motion.RobotLocation.DifferentialDriveRobotLocation
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
        @type reference_speed: motion.RobotSpeed.DifferentialDriveRobotSpeed
        @type location: motion.RobotLocation.DifferentialDriveRobotLocation
        @type global_location: motion.RobotLocation.DifferentialDriveRobotLocation
        @type reference_location: motion.RobotLocation.DifferentialDriveRobotLocation
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


class DifferentialDriveMovementController:
    """
    Class to control the movement of a differential drive mobile robot

    @param movement_supervisor: Object to supervise the movement
    @param trajectory_planner: Object to make the trajectory planning
    @param odometry_localizer: Object to make odometry localization
    @param trajectory_tracker: Object to make the trajectory tracking
    @param motor_handler: Object to handle the motors
    @param robot_parameters: Parameters of the robot
    @param sample_time: Sample time of the control system
    @type sample_time: float
    @type movement_supervisor: motion.MovementSupervisor.DifferentialDriveMovementSupervisor
    @type trajectory_planner: motion.TrajectoryPlanner.DifferentialDriveTrajectoryPlanner
    @type trajectory_tracker: motion.TrajectoryTracker.DifferentialDriveTrajectoryTracker
    @type robot_parameters: motion.RobotParameters.DifferentialDriveRobotParameters
    @type motor_handler: motion.MotorHandler.DifferentialDriveMotorHandler
    @type odometry_localizer: motion.OdometryLocalizer.DifferentialDriveOdometryLocalizer
    """

    def __init__(self, movement_supervisor, trajectory_planner, odometry_localizer, trajectory_tracker, motor_handler,
                 timer, robot_parameters):
        self.ordered_stop = True
        self.sample_time = robot_parameters.sample_time
        self.movement_supervisor = movement_supervisor
        self.robot_parameters = robot_parameters
        self.motor_handler = motor_handler
        self.trajectory_tracker = trajectory_tracker
        self.odometry_localizer = odometry_localizer
        self.trajectory_planner = trajectory_planner
        self.robot_state = DifferentialDriveRobotState()
        self.timer = timer


        self.timer.set_timer_overflow_function(self.closed_loop_movement_control)
        self.prev_time = time.time()

        self.dir = [0, 0, 0]

    def measure_speeds(self, delta_encoder_count_1, delta_encoder_count_2, elapsed_time):
        """
        Measure speeds of both motors of the robot

        @param delta_encoder_count_1: encoder count for motor 1 since last measure
        @param delta_encoder_count_2: encoder count for motor 2 since last measure
        @param elapsed_time: time elapsed since last measure
        @type elapsed_time: float
        @type delta_encoder_count_2: int
        @type delta_encoder_count_1: int
        @rtype : tuple
        @return: The actual speeds of the motors(2 floats)
        """

        if elapsed_time < 0.0000000001:
            elapsed_time = 0.0000000001
            logging.warning('almost dividing by zero') # TODO: Check warning
        steps_per_sec_1 = delta_encoder_count_1 / elapsed_time
        angular_speed_1 = steps_per_sec_1 * 2 * math.pi / self.robot_parameters.steps_per_revolution

        steps_per_sec_2 = delta_encoder_count_2 / elapsed_time
        angular_speed_2 = steps_per_sec_2 * 2 * math.pi / self.robot_parameters.steps_per_revolution

        return angular_speed_1, angular_speed_2

    def movement_init(self, trajectory_parameters=None):
        """
        Initialize the movement

        @type trajectory_parameters: motion.TrajectoryParameters.DifferentialDriveTrajectoryParameters
        @param trajectory_parameters: Parameters for the movement's trajectory
        """
        if trajectory_parameters:
            self.trajectory_planner.initialize_track(trajectory_parameters)
            self.movement_supervisor.movement_begin(self.trajectory_planner.get_length())
        else:
            self.timer.set_timer_overflow_function(self.open_loop_movement_control)
            self.movement_supervisor.movement_begin(None)
        self.motor_handler.reset()
        self.trajectory_tracker.reset()
        # self.odometry_localizer.reset_location()


    def open_loop_movement_control(self):
        """
        Control the movement

        @type elapsed_time: float
        @param elapsed_time: elapsed time since last call
        """
        now = time.time()
        elapsed_time = max(now - self.prev_time, 0.00001) # TODO:Check for very fast processor, never knows :)

        self.prev_time = now

        if self.ordered_stop:
            self.movement_finish()
            return

        delta_encoder_count_1, delta_encoder_count_2, battery_voltage, current_1, current_2 = self.motor_handler. \
            read_delta_encoders_count_state()
        angular_speed_1, angular_speed_2 = self.measure_speeds(delta_encoder_count_1, delta_encoder_count_2,
                                                               elapsed_time)
        self.motor_handler.set_measured_speeds(angular_speed_1, angular_speed_2)

        location, global_position = self.odometry_localizer.update_location(delta_encoder_count_1,
                                                                            delta_encoder_count_2)

        x, y, z = self.get_movement_direction_vector()

        set_point_1, set_point_2 = self.follow(x, y, z)

        self.motor_handler.set_speeds(set_point_1, set_point_2)

        self.robot_state.update(location, global_position, None, None, None, None, angular_speed_1,
                                set_point_1, current_1, angular_speed_2, set_point_2, current_2, battery_voltage,
                                elapsed_time)

        self.movement_supervisor.movement_update(self.robot_state)

    def closed_loop_movement_control(self):
        """
        Control the movement

        @type elapsed_time: float
        @param elapsed_time: elapsed time since last call
        """
        now = time.time()
        elapsed_time = now - self.prev_time
        self.prev_time = now

        if self.trajectory_planner.has_finished() or self.ordered_stop:
            self.movement_finish()
            return

        delta_encoder_count_1, delta_encoder_count_2, battery_voltage, current_1, current_2 = self.motor_handler. \
            read_delta_encoders_count_state()
        angular_speed_1, angular_speed_2 = self.measure_speeds(delta_encoder_count_1, delta_encoder_count_2,
                                                               elapsed_time)
        self.motor_handler.set_measured_speeds(angular_speed_1, angular_speed_2)

        location, global_position = self.odometry_localizer.update_location(delta_encoder_count_1,
                                                                            delta_encoder_count_2)

        reference_location, reference_speed = self.trajectory_planner.get_next_point()

        set_point_1, set_point_2, u1, u2 = self.trajectory_tracker.track(reference_location, reference_speed, location)

        self.motor_handler.set_speeds(set_point_1, set_point_2)

        self.robot_state.update(location, global_position, reference_location, reference_speed, u1, u2, angular_speed_1,
                                set_point_1, current_1, angular_speed_2, set_point_2, current_2, battery_voltage,
                                elapsed_time)

        self.movement_supervisor.movement_update(self.robot_state)

    def follow(self, x, y, z):
        """
        calculate the wheel speeds for an asynchronous event.

        :param x: value of displacement in X axis
        :type x: float
        :param y: value of displacement in Y axis
        :type y: float
        :return: wheel speeds
        :type: tuple

        """
        if not (x, y) == (0, 0):
            left = right = y
            ratio = abs(x / self.robot_parameters.max_speed)
            if x < 0:
                right *= (1 - ratio)
            elif x > 0:
                left *= (1 - ratio)
            return right, left
        elif z:
            return z, -z
        else:
            return 0, 0

    def get_movement_direction_vector(self):
        x, y, z = 0, 0, 0
        # TODO: change 8 for max speed
        dx, dy, dz = [i*8 for i in self.dir]
        # if 87 in keys:  # W
        #     dy += 8
        # if 65 in keys:  # A
        #     dx -= 8
        # if 83 in keys:  # S
        #     dy -= 8
        # if 68 in keys:  # D
        #     dx += 8
        # if 81 in keys:  # Q
        #     dz -= 8
        # if 69 in keys:  # E
        #     dz += 8

        # x = (x+dx)/2.0
        # y = (y+dy)/2.0
        # z = (z+dz)/2.0

        return dx, dy, dz

    def movement_finish(self):
        """
        Finish the movement

        """
        self.timer.timer_stop()
        self.timer.set_timer_overflow_function(self.closed_loop_movement_control)
        self.movement_stop()
        self.motor_handler.stop_motors()
        self.movement_supervisor.movement_end()

    def movement_start(self):
        """
        Start the movement

        """
        self.ordered_stop = False
        self.prev_time = time.time()
        self.timer.timer_init()

    def movement_stop(self):
        """
        Order to stop the movement

        """
        self.ordered_stop = True


