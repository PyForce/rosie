import pytest

from rosie.control.models import Planned
from rosie.control.movement import is_over, planned_step
from rosie.models import STILL, Control, Pose, Tracking, Velocity, Wheels
from rosie.planning.models import Reference

WHEELS = Wheels(radius=0.05, distance=0.3, encoder_steps=360, max_speed=10.0)
CONTROL = Control(0.05, 0.01, 5.0, Tracking(0.1, 1.0, 1.0))
READING = (0.0, 0.0, 12.0, 0.1, 0.2)  # steps, steps, V, A, A


def planned(*poses: Pose) -> Planned:
    return Planned(tuple(Reference(pose, STILL) for pose in poses), 0, 0.0)


def straight_ahead(
    reference: Pose, velocity: Velocity, pose: Pose
) -> tuple[float, float, float, float]:
    return 1.0, 1.0, reference.x - pose.x, velocity.x


def test_a_planned_step_follows_the_next_reference() -> None:
    movement = planned(Pose(0.1, 0, 0), Pose(0.2, 0, 0))
    following, set_points, state = planned_step(
        movement, Pose(0, 0, 0), (0.5, 0.5), READING, 0.05, 1.0, WHEELS, straight_ahead
    )
    assert following.next_index == 1
    assert set_points == (1.0, 1.0)
    assert (state.reference_pose, state.tracker_x, state.battery_voltage) == (
        Pose(0.1, 0, 0),
        0.1,
        12.0,
    )
    assert movement.next_index == 0  # the movement is a value: the step made a new one


def test_the_last_reference_marks_when_the_trajectory_was_done() -> None:
    following, _, _ = planned_step(
        planned(Pose(0.1, 0, 0)), Pose(0, 0, 0), (0, 0), READING, 0.05, 7.0, WHEELS, straight_ahead
    )
    assert following.trajectory_done
    assert following.finished_at == 7.0


def test_after_the_trajectory_it_drives_onto_the_target() -> None:
    done = Planned((Reference(Pose(1, 0, 0), STILL),), 1, 0.0)
    _, (left, right), state = planned_step(
        done, Pose(0, 0, 0), (0, 0), READING, 0.05, 1.0, WHEELS, straight_ahead
    )
    assert left == right > 0  # straight ahead, forward
    assert state.reference_pose == Pose(1, 0, 0)


@pytest.mark.parametrize(
    ("pose", "now", "over"),
    [
        (Pose(1, 0, 0), 1.0, True),  # arrived
        (Pose(0.5, 0, 0), 1.0, False),  # on its way
        (Pose(0.5, 0, 0), 6.0, True),  # too late: arrival_timeout is 5 s
    ],
)
def test_is_over(pose: Pose, now: float, over: bool) -> None:
    done = Planned((Reference(Pose(1, 0, 0), STILL),), 1, 0.0)
    assert is_over(done, pose, now, CONTROL) is over


def test_a_movement_is_not_over_before_its_trajectory_is() -> None:
    assert not is_over(planned(Pose(1, 0, 0)), Pose(1, 0, 0), 100.0, CONTROL)
