import math
from collections.abc import Callable
from pathlib import Path

import pytest

from rosie.const import MAP
from rosie.planning.maps import MAPS_DIR, list_maps
from rosie.profile import Profile, load_profile
from rosie.robot import Robot

HOUSE = MAP.default  # rosie's own map

SAMPLE_TIME = 0.05


class FakeClock:
    """A clock the tests move by hand."""

    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class FakeSerial:
    """A serial port that records what's written and answers from a buffer."""

    def __init__(self) -> None:
        self.written: list[bytes] = []
        self.incoming = bytearray()

    def write(self, data: bytes, /) -> int:
        self.written.append(bytes(data))
        return len(data)

    def read(self, size: int = 1, /) -> bytes:
        chunk = bytes(self.incoming[:size])
        del self.incoming[:size]
        return chunk


class FakeI2C:
    """An I2C bus that records every call and answers reads from queues."""

    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []
        self.bytes_written: list[int] = []
        self.blocks_written: list[list[int]] = []
        self.bytes: list[int] = []
        self.blocks: list[list[int]] = []
        self.failures = 0  # the next reads that raise OSError

    def write_byte(self, address: int, value: int, /) -> None:
        self.calls.append(("write_byte", address, value))
        self.bytes_written.append(value)

    def read_byte(self, address: int, /) -> int:
        self._fail_maybe()
        self.calls.append(("read_byte", address))
        return self.bytes.pop(0) if self.bytes else 0

    def write_byte_data(self, address: int, register: int, value: int, /) -> None:
        self.calls.append(("write_byte_data", address, register, value))

    def write_i2c_block_data(self, address: int, register: int, data: list[int], /) -> None:
        self.calls.append(("write_block", address, register, list(data)))
        self.blocks_written.append(list(data))

    def read_i2c_block_data(self, address: int, register: int, length: int, /) -> list[int]:
        self.calls.append(("read_block", address, register, length))
        return self.blocks.pop(0) if self.blocks else [0] * length

    def _fail_maybe(self) -> None:
        if self.failures:
            self.failures -= 1
            raise OSError("I2C error")


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def simubot_profile() -> Profile:
    return load_profile("simubot")


@pytest.fixture
def maps() -> dict[str, Path]:
    return list_maps([MAPS_DIR])


@pytest.fixture
def robot(simubot_profile: Profile, maps: dict[str, Path], clock: FakeClock) -> Robot:
    return Robot(simubot_profile, maps, HOUSE, None, clock)


@pytest.fixture
def run(clock: FakeClock) -> Callable[[Robot, float], None]:
    """Advance the clock and tick the robot for `seconds`."""

    def advance(robot: Robot, seconds: float) -> None:
        for _ in range(round(seconds / SAMPLE_TIME)):
            clock.now += SAMPLE_TIME
            robot.tick()

    return advance


def distance(robot: Robot, x: float, y: float) -> float:
    rx, ry, _ = robot.position()
    return math.hypot(rx - x, ry - y)
