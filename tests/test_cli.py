import os
import signal
import threading
from pathlib import Path

import pytest
from typer.testing import CliRunner

from rosie import cli, service
from rosie.models import StartSettings

VARIABLES = (
    "ROSIE_ROBOT_PROFILE",
    "ROSIE_MAP",
    "ROSIE_INTERFACES",
    "ROSIE_HOST",
    "ROSIE_PORT",
    "ROSIE_RECORD",
)


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (*VARIABLES, "ROSIE_LOG_LEVEL"):
        monkeypatch.delenv(name, raising=False)


def start(monkeypatch: pytest.MonkeyPatch, *args: str) -> list[StartSettings]:
    """Run `rosie start ARGS` with service.run recorded instead of run."""
    started: list[StartSettings] = []

    async def record(settings: StartSettings) -> None:
        started.append(settings)

    monkeypatch.setattr(service, "run", record)
    result = CliRunner().invoke(cli.app, ["start", *args])
    assert result.exit_code == 0, result.output
    return started


def test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    assert start(monkeypatch) == [
        StartSettings("simubot", "Gustavo's House", ("web",), "0.0.0.0", 5000, None)  # noqa: S104
    ]


def test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROSIE_ROBOT_PROFILE", "kevin")
    monkeypatch.setenv("ROSIE_MAP", "Garage")
    monkeypatch.setenv("ROSIE_INTERFACES", "web, ros")
    monkeypatch.setenv("ROSIE_HOST", "127.0.0.1")
    monkeypatch.setenv("ROSIE_PORT", "6000")
    monkeypatch.setenv("ROSIE_RECORD", "~/runs")
    assert start(monkeypatch) == [
        StartSettings("kevin", "Garage", ("web", "ros"), "127.0.0.1", 6000, Path.home() / "runs")
    ]


def test_flags_beat_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROSIE_ROBOT_PROFILE", "kevin")
    monkeypatch.setenv("ROSIE_PORT", "6000")
    monkeypatch.setenv("ROSIE_INTERFACES", "web")
    (settings,) = start(
        monkeypatch, "--robot-profile", "./my-robot", "--port", "7000", "--interfaces", ""
    )
    assert (settings.profile, settings.port, settings.interfaces) == ("./my-robot", 7000, ())


@pytest.mark.parametrize(
    ("value", "expected"), [("web", ("web",)), ("web, ros", ("web", "ros")), ("", ()), (" , ", ())]
)
def test_interfaces_are_a_comma_separated_list(
    monkeypatch: pytest.MonkeyPatch, value: str, expected: tuple[str, ...]
) -> None:
    (settings,) = start(monkeypatch, "--interfaces", value)
    assert settings.interfaces == expected


def test_help_names_every_variable() -> None:
    output = CliRunner().invoke(cli.app, ["start", "--help"], env={"COLUMNS": "200"}).output
    for name in (*VARIABLES, "ROSIE_LOG_LEVEL"):
        assert name in output


def test_a_wrong_log_level() -> None:
    result = CliRunner().invoke(cli.app, ["start", "--log-level", "loud"], env={"COLUMNS": "200"})
    assert result.exit_code == 2
    assert "'loud' is not one of" in result.output


def test_starts_and_stops_on_a_signal() -> None:
    timer = threading.Timer(0.5, os.kill, (os.getpid(), signal.SIGINT))
    timer.start()
    args = ["start", "--host", "127.0.0.1", "--port", "0", "--log-level", "warning"]
    result = CliRunner().invoke(cli.app, args)
    timer.join()
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["--robot-profile", "nobot"], "rosie: unknown robot profile nobot"),
        (["--robot-profile", "kevin"], "rosie: nothing answers on /dev/ttyACM0"),
        (["--map", "Nowhere"], "rosie: unknown map: Nowhere"),
        (["--interfaces", "ros"], "rosie: unsupported interfaces: ros (known: web)"),
    ],
)
def test_setup_problems_are_one_line(args: list[str], message: str) -> None:
    result = CliRunner().invoke(cli.app, ["start", "--port", "0", *args], env={"COLUMNS": "200"})
    assert result.exit_code == 1
    (line,) = result.output.strip().splitlines()  # no traceback
    assert line.startswith(message)
