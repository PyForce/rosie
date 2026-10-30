import logging
import math
from collections.abc import Callable

from rosie.motion.models import RESTING, RobotParameters, RobotState, TrajectoryParameters
from rosie.motion.motors import MotorHandler
from rosie.motion.odometry import OdometryLocalizer
from rosie.motion.supervisors import MovementSupervisor
from rosie.motion.tracking import TrajectoryTracker
from rosie.motion.trajectories import TrajectoryPlanner

logger = logging.getLogger(__name__)

# wheel speed (rad/s) for a fully pressed key under manual control
MANUAL_SPEED = 8
# s: shorter steps would divide the encoder steps by (almost) zero
MIN_ELAPSED_TIME = 0.0000000001


class MovementController:
    """
    Runs the robot's movements, one control step per tick(): follows the
    planned trajectory (closed loop) or the pressed keys (manual, open loop).
    """

    def __init__(
        self,
        movement_supervisor: MovementSupervisor,
        trajectory_planner: TrajectoryPlanner,
        odometry_localizer: OdometryLocalizer,
        trajectory_tracker: TrajectoryTracker,
        motor_handler: MotorHandler,
        robot_parameters: RobotParameters,
        clock: Callable[[], float],
    ) -> None:
        self.ordered_stop = True
        self.sample_time = robot_parameters.sample_time
        self.movement_supervisor = movement_supervisor
        self.robot_parameters = robot_parameters
        self.clock = clock
        self.motor_handler = motor_handler
        self.trajectory_tracker = trajectory_tracker
        self.odometry_localizer = odometry_localizer
        self.trajectory_planner = trajectory_planner
        self.robot_state = RESTING

        self.running = False
        self.step = self.closed_loop_movement_control
        self.prev_time = self.clock()

        # pressed keys under manual control: x (steer), y (throttle), rotation, each in [-1, 1]
        self.direction = [0.0, 0.0, 0.0]

    def tick(self) -> None:
        if self.running:
            self.step()

    def movement_init(self, trajectory_parameters: TrajectoryParameters | None) -> None:
        """Prepare a planned movement, or manual control when there are no parameters."""
        if trajectory_parameters:
            self.trajectory_planner.initialize_track(trajectory_parameters)
            self.movement_supervisor.movement_begin(self.trajectory_planner.get_length())
        else:
            self.step = self.open_loop_movement_control
            self.movement_supervisor.movement_begin(None)
        self.motor_handler.reset()
        self.trajectory_tracker.reset()

    def movement_start(self) -> None:
        self.ordered_stop = False
        self.prev_time = self.clock()
        self.running = True

    def movement_stop(self) -> None:
        self.ordered_stop = True

    def movement_finish(self) -> None:
        self.running = False
        self.step = self.closed_loop_movement_control
        self.movement_stop()
        self.motor_handler.stop_motors()
        self.movement_supervisor.movement_end()

    def closed_loop_movement_control(self) -> None:
        now = self.clock()
        elapsed_time = now - self.prev_time
        self.prev_time = now

        if self.trajectory_planner.has_finished() or self.ordered_stop:
            self.movement_finish()
            return

        reading = self.motor_handler.read_delta_encoders_count_state()
        if reading is None:
            logger.error("no reading from the motor driver")
            return
        delta_steps_1, delta_steps_2, battery_voltage, current_1, current_2 = reading
        angular_speed_1, angular_speed_2 = self.measure_speeds(
            delta_steps_1, delta_steps_2, elapsed_time
        )
        self.motor_handler.set_measured_speeds(angular_speed_1, angular_speed_2)

        location, global_location = self.odometry_localizer.update_location(
            delta_steps_1, delta_steps_2
        )

        reference_location, reference_speed = self.trajectory_planner.get_next_point()

        set_point_1, set_point_2, u1, u2 = self.trajectory_tracker.track(
            reference_location, reference_speed, location
        )

        self.motor_handler.set_speeds(set_point_1, set_point_2)

        self.robot_state = RobotState(
            location,
            global_location,
            reference_location,
            reference_speed,
            u1,
            u2,
            angular_speed_1,
            set_point_1,
            current_1,
            angular_speed_2,
            set_point_2,
            current_2,
            battery_voltage,
            elapsed_time,
        )

        self.movement_supervisor.movement_update(self.robot_state)

    def open_loop_movement_control(self) -> None:
        now = self.clock()
        elapsed_time = max(now - self.prev_time, 0.00001)
        self.prev_time = now

        if self.ordered_stop:
            self.movement_finish()
            return

        reading = self.motor_handler.read_delta_encoders_count_state()
        if not reading:
            logger.error("no reading from the motor driver")
            return
        delta_steps_1, delta_steps_2, battery_voltage, current_1, current_2 = reading
        angular_speed_1, angular_speed_2 = self.measure_speeds(
            delta_steps_1, delta_steps_2, elapsed_time
        )
        self.motor_handler.set_measured_speeds(angular_speed_1, angular_speed_2)

        location, global_location = self.odometry_localizer.update_location(
            delta_steps_1, delta_steps_2
        )

        set_point_1, set_point_2 = self._wheel_speeds(*self._direction_vector())

        self.motor_handler.set_speeds(set_point_1, set_point_2)

        self.robot_state = RobotState(
            location,
            global_location,
            None,
            None,
            None,
            None,
            angular_speed_1,
            set_point_1,
            current_1,
            angular_speed_2,
            set_point_2,
            current_2,
            battery_voltage,
            elapsed_time,
        )

        self.movement_supervisor.movement_update(self.robot_state)

    def measure_speeds(
        self, delta_steps_1: float, delta_steps_2: float, elapsed_time: float
    ) -> tuple[float, float]:
        if elapsed_time < MIN_ELAPSED_TIME:
            elapsed_time = MIN_ELAPSED_TIME
            logger.warning("almost dividing by zero")
        steps_per_sec_1 = delta_steps_1 / elapsed_time
        angular_speed_1 = steps_per_sec_1 * 2 * math.pi / self.robot_parameters.steps_per_revolution

        steps_per_sec_2 = delta_steps_2 / elapsed_time
        angular_speed_2 = steps_per_sec_2 * 2 * math.pi / self.robot_parameters.steps_per_revolution

        return angular_speed_1, angular_speed_2

    def _direction_vector(self) -> tuple[float, float, float]:
        dx, dy, dz = (key * MANUAL_SPEED for key in self.direction)
        return dx, dy, dz

    def _wheel_speeds(self, x: float, y: float, z: float) -> tuple[float, float]:
        """Racing-game driving: y is the throttle, x steers while moving, z turns on the spot."""
        if (x, y) != (0, 0):
            left = right = y
            ratio = abs(x / self.robot_parameters.max_speed)
            if x < 0:
                right *= 1 - ratio
            elif x > 0:
                left *= 1 - ratio
            return right, left
        if z:
            return z, -z
        return 0, 0
