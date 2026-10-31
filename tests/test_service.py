import asyncio
import dataclasses
import os
import signal
import socket
import time
from collections.abc import Callable
from pathlib import Path

import pytest

from rosie import service
from rosie.errors import HardwareUnavailableError
from rosie.models import Profile, StartSettings
from rosie.profile import BUILTIN_PROFILES
from rosie.robot import build_robot
from rosie.world.maps import BUILTIN_MAPS, DEFAULT_MAP


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port: int = probe.getsockname()[1]
        return port


async def get(port: int, path: str) -> str:
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(f"GET {path} HTTP/1.1\r\nHost: rosie\r\nConnection: close\r\n\r\n".encode())
    response = (await reader.read()).decode()
    writer.close()
    return response


def settings(robot: str, port: int) -> StartSettings:
    return StartSettings(robot, DEFAULT_MAP, ("web",), "127.0.0.1", port, None)


def test_runs_the_robot_and_its_web_api_until_a_signal(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("INFO")
    port = free_port()
    # your robot, with a map of its own next to rosie's
    robot = tmp_path / "my-robot"
    (robot / "maps").mkdir(parents=True)
    (robot / "profile.toml").write_text((BUILTIN_PROFILES / "simubot" / "profile.toml").read_text())
    house = (BUILTIN_MAPS / "house.json").read_text()
    (robot / "maps" / "garage.json").write_text(house.replace(DEFAULT_MAP, "Garage"))

    async def scenario() -> tuple[str, str]:
        running = asyncio.create_task(service.run(settings(str(robot), port)))
        for _ in range(50):
            await asyncio.sleep(0.1)
            try:
                odometry = await get(port, "/odometry")
                break
            except OSError:
                continue
        maps = await get(port, "/maps")
        os.kill(os.getpid(), signal.SIGTERM)
        await asyncio.wait_for(running, 5)
        return odometry, maps

    odometry, maps = asyncio.run(scenario())
    assert odometry.startswith("HTTP/1.1 200")
    assert '"x":0.0' in odometry
    assert '"Garage"' in maps and DEFAULT_MAP in maps
    assert f"web API on http://127.0.0.1:{port}" in caplog.text
    assert caplog.messages[-2:] == ["stopping...", "stopped"]


def test_a_robot_with_an_ultrasound_board_needs_it(tmp_path: Path) -> None:
    (tmp_path / "profile.toml").write_text(
        (BUILTIN_PROFILES / "simubot" / "profile.toml").read_text() + "\n[sensors.usound]\n"
    )
    with pytest.raises(HardwareUnavailableError):  # no I2C bus here
        asyncio.run(service.run(settings(str(tmp_path), free_port())))


def test_the_robot_alone(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("INFO")
    alone = dataclasses.replace(settings("simubot", free_port()), interfaces=())

    async def scenario() -> None:
        running = asyncio.create_task(service.run(alone))
        await asyncio.sleep(0.3)
        os.kill(os.getpid(), signal.SIGTERM)
        await asyncio.wait_for(running, 5)

    asyncio.run(scenario())
    assert "web API" not in caplog.text
    assert caplog.messages[-2:] == ["stopping...", "stopped"]


def test_an_unknown_interface_starts_nothing(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("INFO")
    ros = dataclasses.replace(settings("simubot", free_port()), interfaces=("web", "ros"))
    with pytest.raises(ValueError, match=r"unsupported interfaces: web, ros \(known: web\)"):
        asyncio.run(service.run(ros))
    assert "profile:" not in caplog.text  # not even the robot


def test_control_loop_stops_the_motors_on_the_way_out(simubot_profile: Profile) -> None:
    robot = build_robot(simubot_profile, DEFAULT_MAP, None, time.monotonic)

    async def scenario() -> None:
        robot.goto(1, 0, 2)
        async with service.start_control_loop(robot):
            await asyncio.sleep(0.3)
        assert robot.movement is None  # the movement ended with the loop
        moved = robot.position()
        await asyncio.sleep(0.1)
        assert robot.position() == moved  # no tick after the loop ended

    asyncio.run(scenario())
    assert robot.position()[0] > 0


async def call_for(seconds: float, action: Callable[[], None]) -> None:
    running = asyncio.create_task(service.run_every(0.01, action))
    await asyncio.sleep(seconds)
    running.cancel()


def test_run_every_keeps_the_period() -> None:
    calls: list[float] = []
    asyncio.run(call_for(0.1, lambda: calls.append(time.monotonic())))
    assert 8 <= len(calls) <= 12


def test_run_every_doesnt_rush_after_a_late_call() -> None:
    calls: list[float] = []

    def late_once() -> None:
        calls.append(time.monotonic())
        if len(calls) == 1:
            time.sleep(0.05)  # five periods late

    asyncio.run(call_for(0.1, late_once))
    assert len(calls) <= 8  # 0.05 s lost, the rest at the normal pace
