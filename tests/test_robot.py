import dataclasses
from collections.abc import Callable
from pathlib import Path

import pytest

import rosie.hardware.drive.devices.arduino
import rosie.hardware.drive.devices.md25
from conftest import FakeClock, FakeI2C, FakeSerial, distance
from rosie.core import Robot
from rosie.models import PIDGains, Profile
from rosie.profile import load_profile
from rosie.robot import build_robot
from rosie.world.maps import DEFAULT_MAP

type Run = Callable[[Robot, float], None]


def test_records_planned_movements(
    simubot_profile: Profile, clock: FakeClock, run: Run, tmp_path: Path
) -> None:
    robot = build_robot(simubot_profile, DEFAULT_MAP, tmp_path / "recordings", clock)
    robot.goto(1, 0.5, 0.5)
    run(robot, 4)
    (recording,) = (tmp_path / "recordings").iterdir()
    lines = recording.read_text().splitlines()
    assert lines[0] == "# wheels.radius = 0.05"
    assert "# control.tracking.lookahead = 0.1" in lines
    assert "# control.regulation.gains.angle = 3.0" in lines  # a default, recorded too
    assert lines[13].startswith("time,elapsed,x,y,theta")  # simubot: no drive gains
    assert len(lines) > 14 + 30


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (
            lambda p: dataclasses.replace(
                p, planning=dataclasses.replace(p.planning, planner="spline")
            ),
            "unsupported trajectory planner: spline",
        ),
        (lambda p: dataclasses.replace(p, drive_type="lego"), "unsupported drive: lego"),
    ],
)
def test_unknown_profile_choices(
    simubot_profile: Profile, clock: FakeClock, change: Callable[[Profile], Profile], message: str
) -> None:
    profile = change(simubot_profile)
    with pytest.raises(ValueError, match=message):
        build_robot(profile, DEFAULT_MAP, None, clock)


def test_unknown_sensor(simubot_profile: Profile, clock: FakeClock) -> None:
    profile = dataclasses.replace(simubot_profile, sensors={"sonar": {}})
    with pytest.raises(ValueError, match=r"unsupported sensor: sonar \(known: usound\)"):
        build_robot(profile, DEFAULT_MAP, None, clock)


class StuckArduino(FakeSerial):
    """Answers every state request: the wheels haven't turned, battery full."""

    def write(self, data: bytes, /) -> int:
        if data == b"\xa8":
            self.incoming += b"\xa9" + bytes(8) + bytes([100])
        return super().write(data)


@pytest.fixture
def fake_drives(monkeypatch: pytest.MonkeyPatch) -> tuple[FakeSerial, FakeI2C]:
    serial, bus = StuckArduino(), FakeI2C()
    monkeypatch.setattr(
        rosie.hardware.drive.devices.arduino, "open_serial", lambda port, baudrate: serial
    )
    monkeypatch.setattr(rosie.hardware.drive.devices.md25, "open_i2c", lambda number: bus)
    return serial, bus


def test_arduino_robot(fake_drives: tuple[FakeSerial, FakeI2C], clock: FakeClock, run: Run) -> None:
    serial, _ = fake_drives
    robot = build_robot(load_profile("kevin"), DEFAULT_MAP, None, clock)
    assert serial.written[0][0] == 0xA6  # the board's PID constants
    robot.goto(1, 0, 0.25)
    run(robot, 0.5)
    assert any(
        package[0] == 0xA7 and package != serial.written[0] for package in serial.written
    )  # speeds


def test_md25_robot(fake_drives: tuple[FakeSerial, FakeI2C], clock: FakeClock, run: Run) -> None:
    _, bus = fake_drives
    robot = build_robot(load_profile("rovert"), DEFAULT_MAP, None, clock)
    robot.goto(1, 0, 0.5)
    run(robot, 0.5)
    assert bus.blocks_written[-1][0] > 0  # rosie's PID pushes the wheels that don't move


def test_gives_up_on_a_robot_that_never_arrives(
    fake_drives: tuple[FakeSerial, FakeI2C],
    clock: FakeClock,
    run: Run,
    caplog: pytest.LogCaptureFixture,
) -> None:
    profile = load_profile("kevin")
    robot = build_robot(profile, DEFAULT_MAP, None, clock)  # its wheels never turn
    robot.goto(1, 0, 0.25)  # 4 s: Kevin's top speed is 0.26 m/s
    run(robot, 4 + profile.control.regulation.timeout + 0.5)
    assert "stopping 1.000 m short of (1.00, 0.00)" in caplog.text


def test_cubic_robot(simubot_profile: Profile, clock: FakeClock, run: Run) -> None:
    cubic = dataclasses.replace(
        simubot_profile, planning=dataclasses.replace(simubot_profile.planning, planner="cubic")
    )
    robot = build_robot(cubic, DEFAULT_MAP, None, clock)
    robot.follow([(1.0, 0.0), (1.0, 1.0)], 0.35)
    run(robot, 8)
    assert distance(robot, 1, 1) < 0.01


def test_the_drive_settings_come_from_the_profile(
    simubot_profile: Profile, clock: FakeClock, monkeypatch: pytest.MonkeyPatch
) -> None:
    opened: list[tuple[str, int]] = []

    def open_serial(port: str, baudrate: int) -> FakeSerial:
        opened.append((port, baudrate))
        return StuckArduino()

    monkeypatch.setattr(rosie.hardware.drive.devices.arduino, "open_serial", open_serial)
    arduino = dataclasses.replace(
        simubot_profile,
        drive_type="arduino",
        drive_settings={"port": "/dev/ttyUSB1", "baudrate": 115200},
        drive_gains=PIDGains(kc=1.0, ki=0.5, kd=0.25),
    )
    build_robot(arduino, DEFAULT_MAP, None, clock)
    assert opened == [("/dev/ttyUSB1", 115200)]


def test_an_unknown_drive_setting(simubot_profile: Profile, clock: FakeClock) -> None:
    virtual = dataclasses.replace(simubot_profile, drive_settings={"port": "/dev/ttyACM0"})
    with pytest.raises(ValueError, match=r"\[drive\] of simubot: unknown setting"):
        build_robot(virtual, DEFAULT_MAP, None, clock)


@pytest.mark.parametrize("drive", ["arduino", "md25"])
def test_a_drive_with_a_pid_needs_its_gains(
    simubot_profile: Profile, clock: FakeClock, fake_drives: tuple[FakeSerial, FakeI2C], drive: str
) -> None:
    without = dataclasses.replace(simubot_profile, drive_type=drive)  # simubot has no [drive.gains]
    with pytest.raises(ValueError, match=rf"\[drive.gains\] of simubot: the {drive} drive needs"):
        build_robot(without, DEFAULT_MAP, None, clock)


def test_recordings_name_the_drive_gains(
    simubot_profile: Profile, clock: FakeClock, run: Run, tmp_path: Path
) -> None:
    with_gains = dataclasses.replace(simubot_profile, drive_gains=PIDGains(kc=2.0, ki=1.0, kd=0.5))
    robot = build_robot(with_gains, DEFAULT_MAP, tmp_path, clock)
    robot.goto(1, 0, 0.5)
    run(robot, 4)
    (recording,) = tmp_path.iterdir()
    assert "# drive.gains.kc = 2.0" in recording.read_text().splitlines()
