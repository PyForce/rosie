import dataclasses
import math
from collections.abc import Callable
from pathlib import Path

import pytest

import rosie.robot
from conftest import FakeClock, FakeI2C, FakeSerial, distance
from rosie.const import MAP
from rosie.errors import NoRouteError
from rosie.motion.supervisors import SupervisorContainer
from rosie.profile import Profile, load_profile
from rosie.robot import Robot, movement_controller, robot_parameters

HOUSE = MAP.default  # rosie's own map

type Run = Callable[[Robot, float], None]

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


def test_robots_are_independent(
    robot: Robot, simubot_profile: Profile, maps: dict[str, Path]
) -> None:
    other = Robot(simubot_profile, maps, HOUSE, None, FakeClock())
    other.teleport(1.0, 2.0, 0.5)
    assert robot.position() == (0.0, 0.0, 0.0)


def test_goto_reaches_the_target(robot: Robot, run: Run) -> None:
    robot.go_to(1, 0.5, 4)
    run(robot, 5)
    assert distance(robot, 1, 0.5) < 0.01


def test_goto_after_teleport(robot: Robot, run: Run) -> None:
    robot.teleport(1, 1, 0)
    robot.go_to(2, 1, 3)
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
    robot.go_to_with_planner(7.7, 1.2, 3)
    run(robot, 1)
    assert distance(robot, 1, 1) > 0.05  # no idle first segment
    run(robot, 30)
    assert distance(robot, 7.7, 1.2) < 0.01


def test_planner_refuses_unreachable_targets(robot: Robot) -> None:
    robot.teleport(1, 1, 0)
    with pytest.raises(NoRouteError, match="not found"):
        robot.go_to_with_planner(5, 1, 3)


@pytest.mark.parametrize("t", [0, 0.01])
def test_rejects_times_shorter_than_a_control_step(robot: Robot, t: float) -> None:
    with pytest.raises(ValueError, match="control step"):
        robot.go_to(1, 0, t)
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
    robot.start_open_loop_control()
    robot.add_movement([sum(axis) for axis in zip(*keys, strict=True)])
    run(robot, 1.5)
    assert math.degrees(robot.position()[2]) == pytest.approx(turn, abs=3)


def test_w_drives_forward(robot: Robot, run: Run) -> None:
    robot.start_open_loop_control()
    robot.add_movement(W)
    run(robot, 1.5)
    x, y, theta = robot.position()
    assert x == pytest.approx(0.58, abs=0.05)
    assert (y, theta) == (0, 0)


def test_steering_alone_does_nothing(robot: Robot, run: Run) -> None:
    robot.start_open_loop_control()
    robot.add_movement(A)
    run(robot, 1.5)
    assert robot.position() == (0.0, 0.0, 0.0)


@pytest.mark.parametrize(("key", "sign"), [(Q, 1), (E, -1)], ids=["Q left", "E right"])
def test_q_and_e_turn_on_the_spot(robot: Robot, run: Run, key: list[float], sign: int) -> None:
    robot.start_open_loop_control()
    robot.add_movement(key)
    run(robot, 0.5)
    x, y, theta = robot.position()
    assert (x, y) == pytest.approx((0, 0), abs=1e-9)
    assert sign * theta > 0.5


def test_stop_ends_manual_control(robot: Robot, run: Run) -> None:
    robot.start_open_loop_control()
    robot.add_movement(W)
    run(robot, 0.5)
    robot.stop_open_loop_control()
    before = robot.position()
    run(robot, 1)
    assert robot.position() == before


def test_stop_ends_a_movement(robot: Robot, run: Run) -> None:
    robot.go_to(2, 0, 4)
    run(robot, 1)
    robot.stop()
    before = robot.position()
    run(robot, 1)
    assert robot.position() == before


def test_maps(robot: Robot) -> None:
    assert list(robot.maps()) == [HOUSE]
    assert robot.map_name == HOUSE
    house = robot.get_map(HOUSE)
    assert house is not None
    assert set(house["rooms"]) == {"Dinning Room", "Hall", "Kitchen", "Living Room"}
    assert robot.get_map("Nowhere") is None
    with pytest.raises(ValueError, match="unknown map"):
        robot.use_map("Nowhere")


def test_records_planned_movements(
    simubot_profile: Profile, maps: dict[str, Path], clock: FakeClock, run: Run, tmp_path: Path
) -> None:
    robot = Robot(simubot_profile, maps, HOUSE, tmp_path / "recordings", clock)
    robot.go_to(1, 0.5, 2)
    run(robot, 4)
    (recording,) = (tmp_path / "recordings").iterdir()
    lines = recording.read_text().splitlines()
    assert lines[0] == "# wheel_radius = 0.05"
    assert lines[8].startswith("time,elapsed,x,y,theta")
    assert len(lines) > 9 + 30


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (
            lambda p: dataclasses.replace(p, interpolation="spline"),
            "unsupported interpolation: spline",
        ),
        (lambda p: dataclasses.replace(p, board="lego"), "unsupported board: lego"),
    ],
)
def test_unknown_profile_choices(
    simubot_profile: Profile, clock: FakeClock, change: Callable[[Profile], Profile], message: str
) -> None:
    profile = change(simubot_profile)
    with pytest.raises(ValueError, match=message):
        movement_controller(profile, robot_parameters(profile), SupervisorContainer(), clock)


class StuckArduino(FakeSerial):
    """Answers every state request: the wheels haven't turned, battery full."""

    def write(self, data: bytes, /) -> int:
        if data == b"\xa8":
            self.incoming += b"\xa9" + bytes(8) + bytes([100])
        return super().write(data)


@pytest.fixture
def fake_boards(monkeypatch: pytest.MonkeyPatch) -> tuple[FakeSerial, FakeI2C]:
    serial, bus = StuckArduino(), FakeI2C()
    monkeypatch.setattr(rosie.robot, "open_serial", lambda port, baudrate: serial)
    monkeypatch.setattr(rosie.robot, "open_i2c", lambda number: bus)
    return serial, bus


def test_arduino_robot(
    fake_boards: tuple[FakeSerial, FakeI2C], maps: dict[str, Path], clock: FakeClock, run: Run
) -> None:
    serial, _ = fake_boards
    robot = Robot(load_profile("kevin"), maps, HOUSE, None, clock)
    assert serial.written[0][0] == 0xA6  # the board's PID constants
    robot.go_to(1, 0, 2)
    run(robot, 0.5)
    assert any(
        package[0] == 0xA7 and package != serial.written[0] for package in serial.written
    )  # speeds


def test_md25_robot(
    fake_boards: tuple[FakeSerial, FakeI2C], maps: dict[str, Path], clock: FakeClock, run: Run
) -> None:
    _, bus = fake_boards
    robot = Robot(load_profile("rovert"), maps, HOUSE, None, clock)
    robot.go_to(1, 0, 2)
    run(robot, 0.5)
    assert bus.blocks_written[-1][0] > 0  # rosie's PID pushes the wheels that don't move


def test_gives_up_on_a_robot_that_never_arrives(
    fake_boards: tuple[FakeSerial, FakeI2C],
    maps: dict[str, Path],
    clock: FakeClock,
    run: Run,
    caplog: pytest.LogCaptureFixture,
) -> None:
    profile = load_profile("kevin")
    robot = Robot(profile, maps, HOUSE, None, clock)  # its wheels never turn
    robot.go_to(1, 0, 1)
    run(robot, 1 + profile.arrival_timeout + 0.5)
    assert "stopping 1.000 m short of (1.00, 0.00)" in caplog.text


def test_cubic_robot(
    simubot_profile: Profile, maps: dict[str, Path], clock: FakeClock, run: Run
) -> None:
    robot = Robot(
        dataclasses.replace(simubot_profile, interpolation="cubic"), maps, HOUSE, None, clock
    )
    robot.follow([(1.0, 0.0), (1.0, 1.0)], 3)
    run(robot, 8)
    assert distance(robot, 1, 1) < 0.01
