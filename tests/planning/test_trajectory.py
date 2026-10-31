import math

import pytest

from rosie.models import Pose
from rosie.planning.models import TrajectoryPlanner, TrajectoryRequest
from rosie.planning.trajectory import plan, plan_cubic, plan_linear

SAMPLE_TIME = 0.1


def poses(shape: TrajectoryPlanner, points: list[tuple[float, float]]) -> list[Pose]:
    key_poses = [Pose(0, 0, 0), *(Pose(x, y, 0) for x, y in points)]
    return [
        reference.pose for reference in plan(shape, TrajectoryRequest(key_poses, 1.0, SAMPLE_TIME))
    ]


@pytest.mark.parametrize("shape", [plan_linear, plan_cubic])
def test_ends_on_the_last_point(shape: TrajectoryPlanner) -> None:
    planned = poses(shape, [(1, 0), (1, 1)])
    assert len(planned) == 2 * 10 + 1
    assert (planned[-1].x, planned[-1].y) == pytest.approx((1, 1))


def test_cubic_passes_the_points_and_curves() -> None:
    planned = poses(plan_cubic, [(1, 0), (1, 1)])
    assert (planned[10].x, planned[10].y) == pytest.approx((1, 0))
    # a smooth corner: the curve swings out before it and crosses it at 45 degrees
    assert min(pose.y for pose in planned[:10]) < -0.05
    assert planned[10].theta == pytest.approx(math.pi / 4)


def test_cubic_keeps_still_on_repeated_points() -> None:
    planned = poses(plan_cubic, [(0, 0)])
    assert all((pose.x, pose.y) == pytest.approx((0, 0)) for pose in planned)


@pytest.mark.parametrize("shape", [plan_linear, plan_cubic])
def test_every_stretch_at_the_same_speed(shape: TrajectoryPlanner) -> None:
    # 0.5 m then 2 m at 0.5 m/s: 1 s then 4 s, 10 then 40 control steps of 0.1 s
    key_poses = [Pose(0, 0, 0), Pose(0.5, 0, 0), Pose(0.5, 2, 0)]
    poses, _ = shape(TrajectoryRequest(key_poses, 0.5, SAMPLE_TIME))
    assert len(poses) == 50
    assert (poses[10].x, poses[10].y) == pytest.approx((0.5, 0))  # the second stretch starts
