from collections.abc import Callable

import pytest

import rosie.hardware.sensors.usound
from conftest import FakeI2C
from rosie.hardware.sensors.usound import UltrasoundBoard

ADDRESS = 0x10


@pytest.fixture(autouse=True)
def no_pauses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rosie.hardware.sensors.usound, "RETRY_PAUSE", 0)
    monkeypatch.setattr("time.sleep", lambda _seconds: None)


@pytest.fixture
def bus() -> FakeI2C:
    return FakeI2C()


@pytest.fixture
def board(bus: FakeI2C) -> UltrasoundBoard:
    return UltrasoundBoard(bus, ADDRESS)


def test_commands_go_twice_then_their_arguments(board: UltrasoundBoard, bus: FakeI2C) -> None:
    board.set_period(300)
    assert bus.bytes_written == [0x03, 0x03, 300 & 0xFF, 300 >> 8]
    assert board.period_ms == 300


@pytest.mark.parametrize(
    ("sensor", "status_1", "status_2"),
    [(1, 0x04, 0x80), (5, 0x40, 0x80), (6, 0x00, 0x81), (12, 0x00, 0xC0)],
)
def test_sensor_bits(board: UltrasoundBoard, sensor: int, status_1: int, status_2: int) -> None:
    board.enable_sensor(sensor)
    assert (board.status_1, board.status_2) == (status_1, status_2)
    board.disable_sensor(sensor)
    assert (board.status_1, board.status_2) == (0x00, 0x80)


def test_distances(board: UltrasoundBoard, bus: FakeI2C) -> None:
    assert board.read_distance(1, corrected=False) is None  # off
    board.enable()
    board.enable_sensor(1)
    ticks = 1000
    bus.bytes += [ticks & 0xFF, ticks >> 8, ticks & 0xFF, ticks >> 8]
    assert board.read_distance(1, corrected=False) == 5.91  # 1000 * 0.17 * 347.8 / 10000
    assert board.read_distance(1, corrected=True) == 5.32  # 10 % less under 10 cm


def test_read_all_switches_everything_on(board: UltrasoundBoard, bus: FakeI2C) -> None:
    bus.bytes += [100, 0] * 12
    assert board.read_all() == [0.53] * 12
    assert (board.status_1, board.status_2) == (0x7F, 0xFF)


def test_temperature(board: UltrasoundBoard, bus: FakeI2C) -> None:
    assert board.read_temperature() == 28.0  # LM35 off
    board.enable()
    board.enable_lm35()
    bus.bytes += [0x00, 0x02] * 2  # 512 -> 25.02 C
    board.calibrate(2)
    assert board.temperature == 25.02
    assert board.speed_of_sound == 346.01


def test_status_period_and_address(board: UltrasoundBoard, bus: FakeI2C) -> None:
    bus.bytes += [0x03, 0x81, 0x2C, 0x01]
    board.read_status()
    board.read_period()
    assert (board.status_1, board.status_2, board.period_ms) == (0x03, 0x81, 300)
    board.change_address(0x20)
    assert board.address == 0x20


@pytest.mark.parametrize(
    ("action", "message"),
    [
        (lambda board: board.set_period(59), "at least 60 ms"),
        (lambda board: board.change_address(0x78), "at most 0x77"),
        (lambda board: board.enable_sensor(13), "numbered 1 to 12"),
    ],
)
def test_rejects_bad_values(
    board: UltrasoundBoard, action: Callable[[UltrasoundBoard], None], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        action(board)


def test_reset_restores_the_settings(board: UltrasoundBoard, bus: FakeI2C) -> None:
    board.change_address(0x20)
    board.enable()
    board.set_period(100)
    bus.calls.clear()
    board.reset()
    assert [call[1] for call in bus.calls[:2]] == [
        0x20,
        0x20,
    ]  # the reset goes to the board's address
    assert board.address == 0x20  # given back after the reset
    assert bus.bytes_written[-4:] == [0x03, 0x03, 100, 0]


def test_retries_and_gives_up(
    board: UltrasoundBoard, bus: FakeI2C, caplog: pytest.LogCaptureFixture
) -> None:
    board.enable()
    board.enable_sensor(1)
    bus.failures = 1
    bus.bytes += [100, 0]
    assert board.read_distance(1, corrected=False) == 0.59
    bus.failures = 6
    assert board.read_distance(1, corrected=False) is None
    assert "doesn't answer" in caplog.text


def test_open_sensor(bus: FakeI2C, monkeypatch: pytest.MonkeyPatch) -> None:
    opened: list[int] = []

    def open_i2c(number: int) -> FakeI2C:
        opened.append(number)
        return bus

    monkeypatch.setattr(rosie.hardware.sensors.usound, "open_i2c", open_i2c)
    read = rosie.hardware.sensors.usound.open_sensor({"bus": 3, "address": 0x11})
    assert opened == [3]
    bus.bytes += [100, 0] * 12
    assert read() == [0.53] * 12
    assert bus.calls[0][1] == 0x11


def test_open_sensor_with_an_unknown_setting() -> None:
    with pytest.raises(ValueError, match=r"\[sensors.usound\]: unknown setting"):
        rosie.hardware.sensors.usound.open_sensor({"buss": 3})
