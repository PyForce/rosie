import itertools
import math
from abc import ABC, abstractmethod

from rosie.motion.models import ORIGIN, STILL, Pose, TrajectoryParameters, Velocity


class TrajectoryPlanner(ABC):
    """Turns key poses into one reference pose and velocity per control step."""

    def __init__(self) -> None:
        self.reference_locations: list[Pose] = []
        self.reference_speeds: list[Velocity] = []
        self.current_point_index = 0
        self.finished = False

    def initialize_track(self, params: TrajectoryParameters) -> None:
        self.current_point_index = 0
        self.finished = False
        self.reference_locations, self.reference_speeds = self._plan(params)

    def get_length(self) -> int:
        return len(self.reference_locations)

    def get_next_point(self) -> tuple[Pose, Velocity]:
        if self.current_point_index >= len(self.reference_locations):
            self.finished = True
            return self.reference_locations[-1], self.reference_speeds[-1]

        result = (
            self.reference_locations[self.current_point_index],
            self.reference_speeds[self.current_point_index],
        )

        self.current_point_index += 1
        if self.current_point_index >= len(self.reference_locations):
            self.finished = True

        return result

    def has_finished(self) -> bool:
        return self.finished

    @abstractmethod
    def _plan(self, params: TrajectoryParameters) -> tuple[list[Pose], list[Velocity]]: ...


class LinearTrajectoryPlanner(TrajectoryPlanner):
    def _plan(self, params: TrajectoryParameters) -> tuple[list[Pose], list[Velocity]]:
        segments = len(params.key_poses) - 1
        points_count = int(segments * params.segment_time / params.sample_time)
        poses = [ORIGIN] * points_count
        velocities = [STILL] * points_count

        theta_prev_interval = 0.0
        points_per_segment = int(params.segment_time / params.sample_time)

        for i in range(segments):
            segment_base_index = i * points_per_segment
            start = params.key_poses[i]
            end = params.key_poses[i + 1]

            delta_x = (end.x - start.x) / float(points_per_segment)
            delta_y = (end.y - start.y) / float(points_per_segment)

            speed_x = delta_x / params.sample_time
            speed_y = delta_y / params.sample_time

            theta_interval = math.atan2(speed_y, speed_x)

            diff1 = abs(theta_interval - theta_prev_interval)
            diff2 = abs(theta_interval + 2 * math.pi - theta_prev_interval)
            diff3 = abs(theta_interval - 2 * math.pi - theta_prev_interval)

            if diff2 < diff1:
                if diff2 < diff3:
                    theta_interval += 2 * math.pi
                else:
                    theta_interval -= 2 * math.pi
            elif diff3 < diff1:
                theta_interval += 2 * math.pi

            poses[segment_base_index] = Pose(start.x, start.y, theta_interval)
            velocities[segment_base_index] = Velocity(
                speed_x, speed_y, (theta_interval - theta_prev_interval) / float(params.sample_time)
            )

            theta_prev_interval = theta_interval

            for j in range(1, points_per_segment):
                previous = poses[segment_base_index + j - 1]
                poses[segment_base_index + j] = Pose(
                    previous.x + delta_x, previous.y + delta_y, theta_interval
                )
                velocities[segment_base_index + j] = Velocity(speed_x, speed_y, 0.0)

        return poses, velocities


class CubicTrajectoryPlanner(TrajectoryPlanner):
    def _plan(self, params: TrajectoryParameters) -> tuple[list[Pose], list[Velocity]]:
        points_per_segment = int(params.segment_time / float(params.sample_time))
        segments = len(params.key_poses) - 1
        points_count = points_per_segment * segments
        poses = [ORIGIN] * points_count
        velocities = [STILL] * points_count

        headings = _headings(params.key_poses)
        for j in range(segments):
            x_i = params.key_poses[j].x
            y_i = params.key_poses[j].y
            theta_i = headings[j]
            x_f = params.key_poses[j + 1].x
            y_f = params.key_poses[j + 1].y
            theta_f = headings[j + 1]
            # tangent gain: the segment's length, so the curve leaves and arrives at its pace
            k = math.hypot(x_f - x_i, y_f - y_i)

            alpha_x = k * math.cos(theta_f) - 3 * x_f
            alpha_y = k * math.sin(theta_f) - 3 * y_f
            beta_x = k * math.cos(theta_i) + 3 * x_i
            beta_y = k * math.sin(theta_i) + 3 * y_i

            positions = []
            for i in range(points_per_segment):
                s = i / float(points_per_segment)
                x = (
                    -(s - 1) * (s - 1) * (s - 1) * x_i
                    + s * s * s * x_f
                    + alpha_x * (s * s) * (s - 1)
                    + beta_x * s * ((s - 1) * (s - 1))
                )
                y = (
                    -(s - 1) * (s - 1) * (s - 1) * y_i
                    + s * s * s * y_f
                    + alpha_y * (s * s) * (s - 1)
                    + beta_y * s * ((s - 1) * (s - 1))
                )
                dx = (
                    -3 * (s - 1) * (s - 1) * x_i
                    + 3 * s * s * x_f
                    + alpha_x * (3 * s * s - 2 * s)
                    + beta_x * (3 * s * s - 4 * s + 1)
                )
                dy = (
                    -3 * (s - 1) * (s - 1) * y_i
                    + 3 * s * s * y_f
                    + alpha_y * (3 * s * s - 2 * s)
                    + beta_y * (3 * s * s - 4 * s + 1)
                )
                xd_dot_dot = (
                    -6 * (s - 1) * x_i + 6 * s * x_f + alpha_x * (6 * s - 2) + beta_x * (6 * s - 4)
                )
                yd_dot_dot = (
                    -6 * (s - 1) * y_i + 6 * s * y_f + alpha_y * (6 * s - 2) + beta_y * (6 * s - 4)
                )
                speed_squared = dx * dx + dy * dy
                # standing still (a zero-length segment): no turning either
                dtheta = (
                    (yd_dot_dot * dx - xd_dot_dot * dy) / speed_squared if speed_squared else 0.0
                )
                positions.append((x, y))
                velocities[points_per_segment * j + i] = Velocity(
                    dx / params.segment_time, dy / params.segment_time, dtheta / params.segment_time
                )

            theta = theta_i
            for i, (x, y) in enumerate(positions):
                if i > 0:
                    theta += velocities[points_per_segment * j + i - 1].theta * params.sample_time
                poses[points_per_segment * j + i] = Pose(x, y, theta)

        return poses, velocities


def _headings(key_poses: list[Pose]) -> list[float]:
    """
    The heading at each key pose for the cubic curve: the first keeps its own
    (the robot's), the last points along the last segment, the others along
    the sum of their incoming and outgoing directions.
    """
    points = [(pose.x, pose.y) for pose in key_poses]
    directions = [_unit(b[0] - a[0], b[1] - a[1]) for a, b in itertools.pairwise(points)]
    middle = [
        math.atan2(incoming[1] + outgoing[1], incoming[0] + outgoing[0])
        for incoming, outgoing in itertools.pairwise(directions)
    ]
    last = math.atan2(directions[-1][1], directions[-1][0]) if directions else key_poses[0].theta
    return [key_poses[0].theta, *middle, last][: len(key_poses)]


def _unit(dx: float, dy: float) -> tuple[float, float]:
    length = math.hypot(dx, dy)
    return (dx / length, dy / length) if length else (0.0, 0.0)
