import os
import signal
import sys
import threading
from pathlib import Path

import pytest

from rosie import __main__ as cli
from rosie import service
from rosie.const import OPTIONS
from rosie.models import Settings


def start(monkeypatch: pytest.MonkeyPatch, *args: str) -> list[Settings]:
    """Run `rosie start ARGS` with service.run recorded instead of run."""
    started: list[Settings] = []

    async def record(settings: Settings) -> None:
        started.append(settings)

    monkeypatch.setattr(service, "run", record)
    monkeypatch.setattr(sys, "argv", ["rosie", "start", *args])
    cli.main()
    return started


def test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for option in OPTIONS:
        monkeypatch.delenv(option.env, raising=False)
    assert start(monkeypatch) == [
        Settings("simubot", "Gustavo's House", ("web",), "0.0.0.0", 5000, None)  # noqa: S104
    ]


def test_a_wrong_log_level(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        start(monkeypatch, "--log-level", "loud")
    assert "invalid choice: 'LOUD'" in capsys.readouterr().err


def test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROSIE_ROBOT", "kevin")
    monkeypatch.setenv("ROSIE_MAP", "Garage")
    monkeypatch.setenv("ROSIE_INTERFACES", "web, ros")
    monkeypatch.setenv("ROSIE_HOST", "127.0.0.1")
    monkeypatch.setenv("ROSIE_PORT", "6000")
    monkeypatch.setenv("ROSIE_RECORD", "~/runs")
    assert start(monkeypatch) == [
        Settings("kevin", "Garage", ("web", "ros"), "127.0.0.1", 6000, Path.home() / "runs")
    ]


def test_flags_beat_the_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ROSIE_ROBOT", "kevin")
    monkeypatch.setenv("ROSIE_PORT", "6000")
    monkeypatch.setenv("ROSIE_RECORD", "~/runs")
    monkeypatch.setenv("ROSIE_INTERFACES", "web")
    args = ["--robot", "./my-robot", "--port", "7000", "--record", "", "--interfaces", ""]
    (settings,) = start(monkeypatch, *args)
    assert (settings.robot, settings.port, settings.record) == ("./my-robot", 7000, None)
    assert settings.interfaces == ()


def test_starts_and_stops_on_a_signal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["rosie", "start", "--host", "127.0.0.1", "--port", "0", "--log-level", "warning"],
    )
    timer = threading.Timer(0.5, os.kill, (os.getpid(), signal.SIGINT))
    timer.start()
    cli.main()
    timer.join()


def test_start_without_the_robot_extra(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setitem(sys.modules, "rosie.service", None)  # as if numpy & co weren't installed
    monkeypatch.setattr(sys, "argv", ["rosie", "start"])
    with pytest.raises(SystemExit) as stopped:
        cli.main()
    assert stopped.value.code == 1
    assert "pip install 'pyforce-rosie[robot]'" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("value", "expected"), [("web", ("web",)), ("web, ros", ("web", "ros")), ("", ()), (" , ", ())]
)
def test_interfaces_are_a_comma_separated_list(
    monkeypatch: pytest.MonkeyPatch, value: str, expected: tuple[str, ...]
) -> None:
    (settings,) = start(monkeypatch, "--interfaces", value)
    assert settings.interfaces == expected
