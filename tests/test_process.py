import asyncio
import os
import signal
import socket
from pathlib import Path

import pytest

from rosie import process
from rosie.const import MAP
from rosie.errors import HardwareUnavailableError
from rosie.models import Settings
from rosie.planning.maps import MAPS_DIR
from rosie.profile import PROFILES_DIR

HOUSE = MAP.default  # rosie's own map


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


def settings(robot: str, port: int) -> Settings:
    return Settings(robot, HOUSE, "127.0.0.1", port, None)


def test_runs_the_robot_and_its_web_api_until_a_signal(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("INFO")
    port = free_port()
    # your robot, with a map of its own next to rosie's
    robot = tmp_path / "my-robot"
    (robot / "maps").mkdir(parents=True)
    (robot / "profile.toml").write_text((PROFILES_DIR / "simubot" / "profile.toml").read_text())
    house = (MAPS_DIR / "house.json").read_text()
    (robot / "maps" / "garage.json").write_text(house.replace(HOUSE, "Garage"))

    async def scenario() -> tuple[str, str]:
        running = asyncio.create_task(process.run(settings(str(robot), port)))
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
    assert '"Garage"' in maps and HOUSE in maps
    assert f"web API on http://127.0.0.1:{port}" in caplog.text
    assert caplog.messages[-2:] == ["stopping...", "stopped"]


def test_a_robot_with_an_ultrasound_board_needs_it(tmp_path: Path) -> None:
    (tmp_path / "profile.toml").write_text(
        (PROFILES_DIR / "simubot" / "profile.toml").read_text() + "\n[sensors.usound]\n"
    )
    with pytest.raises(HardwareUnavailableError):  # no smbus2 here
        asyncio.run(process.run(settings(str(tmp_path), free_port())))
