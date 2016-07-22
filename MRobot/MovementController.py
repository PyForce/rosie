import math
import signal
import time
from MRobot.RobotState import DifferentialDriveRobotState

__author__ = 'Silvio'


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
    @type movement_supervisor: MRobot.MovementSupervisor.DifferentialDriveMovementSupervisor
    @type trajectory_planner: MRobot.TrajectoryPlanner.DifferentialDriveTrajectoryPlanner
    @type trajectory_tracker: MRobot.TrajectoryTracker.DifferentialDriveTrajectoryTracker
    @type robot_parameters: MRobot.RobotParameters.DifferentialDriveRobotParameters
    @type motor_handler: MRobot.MotorHandler.DifferentialDriveMotorHandler
    @type odometry_localizer: MRobot.OdometryLocalizer.DifferentialDriveOdometryLocalizer
    """

    def __init__(self, movement_supervisor, trajectory_planner, odometry_localizer, trajectory_tracker, motor_handler,
                 robot_parameters, sample_time):
        self.ordered_stop = True
        self.sample_time = sample_time
        self.movement_supervisor = movement_supervisor
        self.robot_parameters = robot_parameters
        self.motor_handler = motor_handler
        self.trajectory_tracker = trajectory_tracker
        self.odometry_localizer = odometry_localizer
        self.trajectory_planner = trajectory_planner
        self.robot_state = DifferentialDriveRobotState()

        self.prev_time = 0
        self.timer_init()

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
        steps_per_sec_1 = delta_encoder_count_1 / elapsed_time
        angular_speed_1 = steps_per_sec_1 * 2 * math.pi / self.robot_parameters.steps_per_revolution

        steps_per_sec_2 = delta_encoder_count_2 / elapsed_time
        angular_speed_2 = steps_per_sec_2 * 2 * math.pi / self.robot_parameters.steps_per_revolution

        return angular_speed_1, angular_speed_2

    def movement_init(self, trajectory_parameters):
        """
        Initialize the movement

        @type trajectory_parameters: MRobot.TrajectoryParameters.DifferentialDriveTrajectoryParameters
        @param trajectory_parameters: Parameters for the movement's trajectory
        """
        self.motor_handler.reset()
        self.trajectory_tracker.reset()
        self.odometry_localizer.reset_location()
        self.trajectory_planner.initialize_track(trajectory_parameters)
        self.movement_supervisor.movement_begin(self.trajectory_planner.get_length())

    def movement_control(self, elapsed_time):
        """
        Control the movement

        @type elapsed_time: float
        @param elapsed_time: elapsed time since last call
        """
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

    def movement_finish(self):
        """
        Finish the movement

        """
        self.motor_handler.stop_motors()
        self.movement_supervisor.movement_end()
        self.timer_stop()

    def movement_start(self):
        """
        Start the movement

        """
        self.ordered_stop = False
        self.prev_time = time.time()
        signal.setitimer(signal.ITIMER_REAL, self.sample_time, self.sample_time)

    def movement_stop(self):
        """
        Order to stop the movement

        """
        self.ordered_stop = True

    def timer_init(self):
        """
        Init the timer

        """
        signal.signal(signal.SIGALRM, self.timer_handler)
        signal.setitimer(signal.ITIMER_REAL, 0, 0)

    def timer_handler(self, signum, frame):
        """
        Handle the time

        @param frame: Stack Frame
        @param signum: Signal number
        """
        now = time.time()
        elapsed = now - self.prev_time
        self.prev_time = now

        self.movement_control(elapsed)

    def timer_stop(self):
        """
        Stop the timer

        """
        signal.setitimer(signal.ITIMER_REAL, 0, 0)
