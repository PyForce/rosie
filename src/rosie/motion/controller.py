import logging
import math

from rosie.boards.models import Board
from rosie.motion.models import (
    ORIGIN,
    RESTING,
    STILL,
    Clock,
    Control,
    Pose,
    Reference,
    RobotState,
    Tracker,
    TrajectoryParameters,
    TrajectoryShape,
    Wheels,
)
from rosie.motion.odometry import advance
from rosie.motion.supervisors import MovementSupervisor
from rosie.motion.trajectories import plan

logger = logging.getLogger(__name__)

# wheel speed (rad/s) for a fully pressed key under manual control
MANUAL_SPEED = 8
# polar go-to-point controller for the end of a planned movement (1/s)
APPROACH_GAIN_DISTANCE = 1.0
APPROACH_GAIN_ANGLE = 3.0
# s: shorter steps would divide the encoder steps by (almost) zero
MIN_ELAPSED_TIME = 0.0000000001


class MotionController:
    """
    Runs the robot's movements, one control step per tick(): follows the
    planned trajectory (closed loop) or the pressed keys (manual, open loop).
    """

    def __init__(
        self,
        supervisors: MovementSupervisor,
        shape: TrajectoryShape,
        track: Tracker,
        board: Board,
        wheels: Wheels,
        control: Control,
        clock: Clock,
    ) -> None:
        self.stop_requested = True
        self.sample_time = control.sample_time
        self.supervisors = supervisors
        self.wheels = wheels
        self.control = control
        self.clock = clock
        self.board = board
        self.shape = shape
        self.track = track
        self.pose = ORIGIN
        # the planned movement: one reference per control step, and the next one to follow
        self.references: list[Reference] = []
        self.next_index = 0
        self.robot_state = RESTING

        self.running = False
        self.step = self.planned_step
        self.prev_time = self.clock()
        self.finished_planning_at = self.prev_time

        # pressed keys under manual control: x (steer), y (throttle), rotation, each in [-1, 1]
        self.direction = [0.0, 0.0, 0.0]

    def tick(self) -> None:
        if self.running:
            self.step()

    def start_planned(self, trajectory: TrajectoryParameters) -> None:
        self.references = plan(self.shape, trajectory)
        self.next_index = 0
        self.supervisors.movement_begin(len(self.references))
        self._start()

    def start_manual(self) -> None:
        self.step = self.manual_step
        self.supervisors.movement_begin(None)
        self._start()

    def finish(self) -> None:
        self.running = False
        self.step = self.planned_step
        self.stop_requested = True
        self.board.stop()
        self.supervisors.movement_end()

    def planned_step(self) -> None:
        now = self.clock()
        elapsed_time = now - self.prev_time
        self.prev_time = now

        if self.stop_requested:
            self.finish()
            return

        if self.trajectory_done:
            target = self.references[-1].pose
            if self._arrived(target) or self._overtime(now):
                self.finish()
                return

        measured = self._measure(elapsed_time)
        if measured is None:
            return
        location, angular_speed_1, angular_speed_2, battery_voltage, current_1, current_2 = measured

        if self.trajectory_done:
            target = self.references[-1].pose
            set_point_1, set_point_2 = approach_speeds(location, target, self.wheels)
            self.board.set_speeds(set_point_1, set_point_2, angular_speed_1, angular_speed_2)
            self.robot_state = RobotState(
                location,
                target,
                STILL,
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
            self.supervisors.movement_update(self.robot_state)
            return

        reference = self.references[self.next_index]
        self.next_index += 1
        reference_location, reference_speed = reference.pose, reference.velocity
        if self.trajectory_done:
            self.finished_planning_at = now

        set_point_1, set_point_2, u1, u2 = self.track(reference_location, reference_speed, location)

        self.board.set_speeds(set_point_1, set_point_2, angular_speed_1, angular_speed_2)

        self.robot_state = RobotState(
            location,
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

        self.supervisors.movement_update(self.robot_state)

    def manual_step(self) -> None:
        now = self.clock()
        elapsed_time = max(now - self.prev_time, 0.00001)
        self.prev_time = now

        if self.stop_requested:
            self.finish()
            return

        measured = self._measure(elapsed_time)
        if measured is None:
            return
        location, angular_speed_1, angular_speed_2, battery_voltage, current_1, current_2 = measured

        set_point_1, set_point_2 = manual_speeds(self.direction, self.wheels.max_speed)

        self.board.set_speeds(set_point_1, set_point_2, angular_speed_1, angular_speed_2)

        self.robot_state = RobotState(
            location,
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

        self.supervisors.movement_update(self.robot_state)

    @property
    def trajectory_done(self) -> bool:
        return self.next_index >= len(self.references)

    def _start(self) -> None:
        self.board.reset()
        self.stop_requested = False
        self.prev_time = self.clock()
        self.running = True

    def _measure(
        self, elapsed_time: float
    ) -> tuple[Pose, float, float, float, float, float] | None:
        """Read the encoders: (pose, wheel speeds, battery voltage, motor currents)."""
        reading = self.board.read_encoders()
        if not reading:
            logger.error("no reading from the motor driver")
            return None
        delta_steps_1, delta_steps_2, battery_voltage, current_1, current_2 = reading
        angular_speed_1, angular_speed_2 = encoder_speeds(
            self.wheels, delta_steps_1, delta_steps_2, elapsed_time
        )
        self.pose = advance(self.pose, self.wheels, delta_steps_1, delta_steps_2)
        location = self.pose
        return location, angular_speed_1, angular_speed_2, battery_voltage, current_1, current_2

    def _arrived(self, target: Pose) -> bool:
        pose = self.pose
        return math.hypot(pose.x - target.x, pose.y - target.y) <= self.control.arrival_tolerance

    def _overtime(self, now: float) -> bool:
        if now - self.finished_planning_at <= self.control.arrival_timeout:
            return False
        pose, target = self.pose, self.references[-1].pose
        logger.warning(
            "stopping %.3f m short of (%.2f, %.2f): not there %.1f s after the planned time",
            math.hypot(pose.x - target.x, pose.y - target.y),
            target.x,
            target.y,
            self.control.arrival_timeout,
        )
        return True


def approach_speeds(pose: Pose, target: Pose, wheels: Wheels) -> tuple[float, float]:
    """
    Wheel speeds towards `target` once the planned trajectory is over: a polar
    go-to-point controller, which brings the wheel axis onto the point (a
    trajectory tracker can't hold a two-wheeled robot on a point).
    """
    distance = math.hypot(target.x - pose.x, target.y - pose.y)
    angle = _wrap(math.atan2(target.y - pose.y, target.x - pose.x) - pose.theta)
    direction = 1.0
    if abs(angle) > math.pi / 2:
        # the target is behind: back up instead of turning around
        angle = _wrap(angle + math.pi)
        direction = -1.0
    v = direction * APPROACH_GAIN_DISTANCE * distance * math.cos(angle)
    omega = APPROACH_GAIN_ANGLE * angle
    radius = wheels.radius
    half_axis = wheels.distance / 2
    limit = wheels.max_speed
    return (
        _clamp((v - omega * half_axis) / radius, limit),
        _clamp((v + omega * half_axis) / radius, limit),
    )


def manual_speeds(keys: list[float], max_speed: float) -> tuple[float, float]:
    """
    Racing-game driving from the pressed keys (each in [-1, 1]): y is the throttle,
    x steers while moving, z turns on the spot.
    """
    x, y, z = (key * MANUAL_SPEED for key in keys)
    if (x, y) != (0, 0):
        left = right = y
        ratio = abs(x / max_speed)
        if x < 0:
            right *= 1 - ratio
        elif x > 0:
            left *= 1 - ratio
        return right, left
    if z:
        return z, -z
    return 0, 0


def encoder_speeds(
    wheels: Wheels, delta_steps_1: float, delta_steps_2: float, elapsed_time: float
) -> tuple[float, float]:
    """Both wheels' speeds (rad/s) from the encoder steps they turned in `elapsed_time`."""
    if elapsed_time < MIN_ELAPSED_TIME:
        elapsed_time = MIN_ELAPSED_TIME
        logger.warning("almost dividing by zero")
    steps_per_sec_1 = delta_steps_1 / elapsed_time
    angular_speed_1 = steps_per_sec_1 * 2 * math.pi / wheels.encoder_steps

    steps_per_sec_2 = delta_steps_2 / elapsed_time
    angular_speed_2 = steps_per_sec_2 * 2 * math.pi / wheels.encoder_steps

    return angular_speed_1, angular_speed_2


def _wrap(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def _clamp(speed: float, limit: float) -> float:
    return max(-limit, min(limit, speed))
