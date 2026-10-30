import math
import time
import logging

from rosie.motion.geometry import DifferentialDriveRobotState

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
                 robot_parameters):
        self.ordered_stop = True
        self.sample_time = robot_parameters.sample_time
        self.movement_supervisor = movement_supervisor
        self.robot_parameters = robot_parameters
        self.motor_handler = motor_handler
        self.trajectory_tracker = trajectory_tracker
        self.odometry_localizer = odometry_localizer
        self.trajectory_planner = trajectory_planner
        self.robot_state = DifferentialDriveRobotState()

        # the control step tick() runs while a movement is active
        self.running = False
        self.step = self.closed_loop_movement_control
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
            self.step = self.open_loop_movement_control
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


        status = self.motor_handler.read_delta_encoders_count_state()
        
        if status:
            delta_encoder_count_1, delta_encoder_count_2, battery_voltage, current_1, current_2 = status
            angular_speed_1, angular_speed_2 = self.measure_speeds(delta_encoder_count_1, delta_encoder_count_2,elapsed_time)
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

        else:
            print("MOTOR CONTROLER ERROR!!!!!!")

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
        self.running = False
        self.step = self.closed_loop_movement_control
        self.movement_stop()
        self.motor_handler.stop_motors()
        self.movement_supervisor.movement_end()

    def movement_start(self):
        """
        Start the movement

        """
        self.ordered_stop = False
        self.prev_time = time.time()
        self.running = True

    def movement_stop(self):
        """
        Order to stop the movement

        """
        self.ordered_stop = True

    def tick(self):
        """
        Run one control step, if a movement is active

        """
        if self.running:
            self.step()
