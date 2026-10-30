import math

import pytest

from rosie.motion.models import Pose, TrajectoryParameters
from rosie.motion.trajectories import CubicTrajectoryPlanner, LinearTrajectoryPlanner

SAMPLE_TIME = 0.1


def plan(
    planner_type: type[LinearTrajectoryPlanner | CubicTrajectoryPlanner],
    points: list[tuple[float, float]],
) -> list[Pose]:
    planner = planner_type()
    planner.initialize_track(
        TrajectoryParameters([Pose(0, 0, 0), *(Pose(x, y, 0) for x, y in points)], 1.0, SAMPLE_TIME)
    )
    poses = []
    while not planner.has_finished():
        pose, _ = planner.get_next_point()
        poses.append(pose)
    return poses


@pytest.mark.parametrize("planner_type", [LinearTrajectoryPlanner, CubicTrajectoryPlanner])
def test_ends_on_the_last_point(
    planner_type: type[LinearTrajectoryPlanner | CubicTrajectoryPlanner],
) -> None:
    poses = plan(planner_type, [(1, 0), (1, 1)])
    assert len(poses) == 2 * 10 + 1
    assert (poses[-1].x, poses[-1].y) == pytest.approx((1, 1))


def test_cubic_passes_the_points_and_curves() -> None:
    poses = plan(CubicTrajectoryPlanner, [(1, 0), (1, 1)])
    assert (poses[10].x, poses[10].y) == pytest.approx((1, 0))
    # a smooth corner: the curve swings out before it and crosses it at 45 degrees
    assert min(pose.y for pose in poses[:10]) < -0.05
    assert poses[10].theta == pytest.approx(math.pi / 4)


def test_cubic_keeps_still_on_repeated_points() -> None:
    poses = plan(CubicTrajectoryPlanner, [(0, 0)])
    assert all((pose.x, pose.y) == pytest.approx((0, 0)) for pose in poses)
