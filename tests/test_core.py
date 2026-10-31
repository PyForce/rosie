import math
from collections.abc import Callable

import pytest

from conftest import FakeClock, distance
from rosie.core import Robot
from rosie.errors import NoRouteError
from rosie.models import Profile
from rosie.planning.path.maps import DEFAULT_MAP
from rosie.robot import build_robot

type Run = Callable[[Robot, float], None]

# what WebRosie sends for each key: steering, throttle, spin
W, S, A, D, Q, E = (
    [0.0, 1.0, 0.0],
    [0.0, -1.0, 0.0],
    [-1.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [0.0, 0.0, -1.0],
    [0.0, 0.0, 1.0],
)


def test_starts_at_the_origin(robot: Robot) -> None:
    assert robot.position() == (0.0, 0.0, 0.0)


def test_robots_are_independent(robot: Robot, simubot_profile: Profile) -> None:
    other = build_robot(simubot_profile, DEFAULT_MAP, None, FakeClock())
    other.teleport(1.0, 2.0, 0.5)
    assert robot.position() == (0.0, 0.0, 0.0)


def test_goto_reaches_the_target(robot: Robot, run: Run) -> None:
    robot.goto(1, 0.5, 4)
    run(robot, 5)
    assert distance(robot, 1, 0.5) < 0.01


def test_goto_after_teleport(robot: Robot, run: Run) -> None:
    robot.teleport(1, 1, 0)
    robot.goto(2, 1, 3)
    run(robot, 5)
    assert distance(robot, 2, 1) < 0.01


def test_follow_passes_every_point(robot: Robot, run: Run, clock: FakeClock) -> None:
    path = [(1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    robot.follow(path, 2)
    closest = dict.fromkeys(path, math.inf)
    for _ in range(int(8 / 0.05)):
        run(robot, 0.05)
        for point in path:
            closest[point] = min(closest[point], distance(robot, *point))
    assert closest[(1.0, 0.0)] < 0.2
    assert closest[(1.0, 1.0)] < 0.2
    assert closest[(0.0, 1.0)] < 0.01


def test_too_fast_follow_still_arrives(robot: Robot, run: Run) -> None:
    robot.follow([(1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], 1)
    run(robot, 3)
    assert distance(robot, 0, 1) > 0.1  # the planned time is too short
    run(robot, 5)
    assert distance(robot, 0, 1) < 0.01


def test_planner_crosses_rooms(robot: Robot, run: Run) -> None:
    robot.teleport(1, 1, 0)
    robot.goto_with_planner(7.7, 1.2, 3)
    run(robot, 1)
    assert distance(robot, 1, 1) > 0.05  # no idle first segment
    run(robot, 30)
    assert distance(robot, 7.7, 1.2) < 0.01


def test_planner_refuses_unreachable_targets(robot: Robot) -> None:
    robot.teleport(1, 1, 0)
    with pytest.raises(NoRouteError, match="not found"):
        robot.goto_with_planner(5, 1, 3)


@pytest.mark.parametrize("t", [0, 0.01])
def test_rejects_times_shorter_than_a_control_step(robot: Robot, t: float) -> None:
    with pytest.raises(ValueError, match="control step"):
        robot.goto(1, 0, t)
    with pytest.raises(ValueError, match="control step"):
        robot.follow([(1, 0)], t)


@pytest.mark.parametrize(
    ("keys", "turn"),
    [
        pytest.param([W, A], 46, id="W+A forward left"),
        pytest.param([W, D], -46, id="W+D forward right"),
        pytest.param([S, A], -46, id="S+A reverse, like a car"),
        pytest.param([S, D], 46, id="S+D reverse, like a car"),
    ],
)
def test_steering_needs_throttle(
    robot: Robot, run: Run, keys: list[list[float]], turn: float
) -> None:
    robot.start_manual()
    robot.move(*(sum(axis) for axis in zip(*keys, strict=True)))
    run(robot, 1.5)
    assert math.degrees(robot.position()[2]) == pytest.approx(turn, abs=3)


def test_w_drives_forward(robot: Robot, run: Run) -> None:
    robot.start_manual()
    robot.move(*W)
    run(robot, 1.5)
    x, y, theta = robot.position()
    assert x == pytest.approx(0.58, abs=0.05)
    assert (y, theta) == (0, 0)


def test_steering_alone_does_nothing(robot: Robot, run: Run) -> None:
    robot.start_manual()
    robot.move(*A)
    run(robot, 1.5)
    assert robot.position() == (0.0, 0.0, 0.0)


@pytest.mark.parametrize(("key", "sign"), [(Q, 1), (E, -1)], ids=["Q left", "E right"])
def test_q_and_e_turn_on_the_spot(robot: Robot, run: Run, key: list[float], sign: int) -> None:
    robot.start_manual()
    robot.move(*key)
    run(robot, 0.5)
    x, y, theta = robot.position()
    assert (x, y) == pytest.approx((0, 0), abs=1e-9)
    assert sign * theta > 0.5


def test_stop_ends_manual_control(robot: Robot, run: Run) -> None:
    robot.start_manual()
    robot.move(*W)
    run(robot, 0.5)
    robot.stop_manual()
    before = robot.position()
    run(robot, 1)
    assert robot.position() == before


def test_stop_ends_a_movement(robot: Robot, run: Run) -> None:
    robot.goto(2, 0, 4)
    run(robot, 1)
    robot.stop()
    before = robot.position()
    run(robot, 1)
    assert robot.position() == before


def test_maps(robot: Robot) -> None:
    assert list(robot.maps()) == [DEFAULT_MAP]
    assert robot.map_name == DEFAULT_MAP
    house = robot.get_map(DEFAULT_MAP)
    assert house is not None
    assert set(house["rooms"]) == {"Dinning Room", "Hall", "Kitchen", "Living Room"}
    assert robot.get_map("Nowhere") is None
    with pytest.raises(ValueError, match="unknown map"):
        robot.use_map("Nowhere")


def test_a_manual_session_starts_standing_still(robot: Robot, run: Run) -> None:
    robot.start_manual()
    robot.move(*W)
    run(robot, 0.5)
    robot.stop_manual()
    moved = robot.position()
    robot.start_manual()  # no keys yet: the previous session's W is gone
    run(robot, 0.5)
    assert robot.position() == moved


def test_keys_outside_manual_control_are_ignored(robot: Robot, run: Run) -> None:
    robot.move(*W)
    robot.start_manual()
    run(robot, 0.5)
    assert robot.position() == (0.0, 0.0, 0.0)
