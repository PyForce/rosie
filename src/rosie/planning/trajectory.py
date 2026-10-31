import itertools
import math

from rosie.models import STILL, Pose, Velocity
from rosie.planning.models import TrajectoryPlanner, TrajectoryPoint, TrajectoryRequest


def plan(planner: TrajectoryPlanner, trajectory: TrajectoryRequest) -> list[TrajectoryPoint]:
    """One reference pose and velocity per control step, ending on the last key pose, standing."""
    poses, velocities = planner(trajectory)
    target = trajectory.key_poses[-1]
    heading = poses[-1].theta if poses else target.theta
    return [
        *(
            TrajectoryPoint(pose, velocity)
            for pose, velocity in zip(poses, velocities, strict=True)
        ),
        TrajectoryPoint(Pose(target.x, target.y, heading), STILL),
    ]


def plan_linear(request: TrajectoryRequest) -> tuple[list[Pose], list[Velocity]]:
    """Straight lines from key pose to key pose, at the request's speed, turning on the spot at each."""
    poses: list[Pose] = []
    velocities: list[Velocity] = []
    theta_prev_interval = 0.0
    for start, end in itertools.pairwise(request.key_poses):
        steps = int(_stretch_time(start, end, request.speed) / request.sample_time)
        if steps == 0:
            continue

        delta_x = (end.x - start.x) / float(steps)
        delta_y = (end.y - start.y) / float(steps)

        speed_x = delta_x / request.sample_time
        speed_y = delta_y / request.sample_time

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

        poses.append(Pose(start.x, start.y, theta_interval))
        velocities.append(
            Velocity(speed_x, speed_y, (theta_interval - theta_prev_interval) / request.sample_time)
        )
        theta_prev_interval = theta_interval

        for _ in range(1, steps):
            previous = poses[-1]
            poses.append(Pose(previous.x + delta_x, previous.y + delta_y, theta_interval))
            velocities.append(Velocity(speed_x, speed_y, 0.0))

    return poses, velocities


def plan_cubic(request: TrajectoryRequest) -> tuple[list[Pose], list[Velocity]]:
    """Cubic polynomials through the key poses, which round the corners, at the request's speed."""
    poses: list[Pose] = []
    velocities: list[Velocity] = []
    headings = _headings(request.key_poses)
    for j, (start, end) in enumerate(itertools.pairwise(request.key_poses)):
        segment_time = _stretch_time(start, end, request.speed)
        steps = int(segment_time / request.sample_time)
        if steps == 0:
            continue
        x_i, y_i, theta_i = start.x, start.y, headings[j]
        x_f, y_f, theta_f = end.x, end.y, headings[j + 1]
        # tangent gain: the segment's length, so the curve leaves and arrives at its pace
        k = math.hypot(x_f - x_i, y_f - y_i)

        alpha_x = k * math.cos(theta_f) - 3 * x_f
        alpha_y = k * math.sin(theta_f) - 3 * y_f
        beta_x = k * math.cos(theta_i) + 3 * x_i
        beta_y = k * math.sin(theta_i) + 3 * y_i

        theta = theta_i
        for i in range(steps):
            s = i / float(steps)
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
            # standing still at that point of the curve: no turning either
            dtheta = (yd_dot_dot * dx - xd_dot_dot * dy) / speed_squared if speed_squared else 0.0
            if i > 0:
                theta += velocities[-1].theta * request.sample_time
            poses.append(Pose(x, y, theta))
            velocities.append(Velocity(dx / segment_time, dy / segment_time, dtheta / segment_time))

    return poses, velocities


def _stretch_time(start: Pose, end: Pose, speed: float) -> float:
    """s to drive from one key pose to the next, along the straight line between them."""
    return math.hypot(end.x - start.x, end.y - start.y) / speed


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


TRAJECTORY_PLANNERS: dict[str, TrajectoryPlanner] = {"linear": plan_linear, "cubic": plan_cubic}
