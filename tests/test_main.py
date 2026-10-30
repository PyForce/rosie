import asyncio
import configparser
import os
import signal
import socket
import sys
import threading
from pathlib import Path

import pytest

from rosie import __main__ as cli


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port: int = probe.getsockname()[1]
        return port


def config(text: str) -> configparser.ConfigParser:
    parsed = configparser.ConfigParser(interpolation=None)
    parsed.read_string(text)
    return parsed


async def get(port: int, path: str) -> str:
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(f"GET {path} HTTP/1.1\r\nHost: rosie\r\nConnection: close\r\n\r\n".encode())
    response = (await reader.read()).decode()
    writer.close()
    return response


def test_runs_its_plugins_until_a_signal(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("INFO")
    port = free_port()
    settings = config(f"""
[general]
profile = simubot
# empty user folders: rosie's own profiles and maps still load
profiles = {tmp_path}
maps = {tmp_path}
[web]
active = True
host = 127.0.0.1
port = {port}
[usound]
active = True
[sonar]
active = True
[recording]
active = False
""")

    async def scenario() -> str:
        running = asyncio.create_task(cli.run(settings))
        for _ in range(50):
            await asyncio.sleep(0.1)
            try:
                response = await get(port, "/odometry")
                break
            except OSError:
                continue
        os.kill(os.getpid(), signal.SIGTERM)
        await asyncio.wait_for(running, 5)
        return response

    response = asyncio.run(scenario())
    assert response.startswith("HTTP/1.1 200")
    assert '"x":0.0' in response
    assert "loaded web" in caplog.text
    assert "unknown section [sonar], known: web, usound" in caplog.text
    assert "plugin usound failed" in caplog.text  # no smbus2 here
    assert caplog.messages[-2:] == ["stopping...", "stopped"]


def test_main_writes_a_config_and_starts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "config.ini"
    path.write_text("[general]\nprofile = simubot\nloglevel = warning\n")
    monkeypatch.setattr(sys, "argv", ["rosie", "--config", str(path), "start"])
    timer = threading.Timer(0.5, os.kill, (os.getpid(), signal.SIGINT))
    timer.start()
    cli.main()
    timer.join()
