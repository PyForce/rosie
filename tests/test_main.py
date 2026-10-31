import sys

import pytest

from rosie import __main__ as entry


def test_without_the_robot_extra(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "rosie.cli", None)  # as if typer, numpy & co weren't installed
    with pytest.raises(SystemExit) as stopped:
        entry.main()
    assert "pip install 'pyforce-rosie[robot]'" in str(stopped.value.code)


def test_runs_the_command_line(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["rosie", "--help"])
    with pytest.raises(SystemExit) as stopped:
        entry.main()
    assert stopped.value.code == 0
