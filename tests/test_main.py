import os
import signal
import sys
import threading
from pathlib import Path

import pytest

from rosie import __main__ as cli


def test_main_writes_a_config_and_starts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "config.ini"
    path.write_text("[general]\nprofile = simubot\nloglevel = warning\n")
    monkeypatch.setattr(sys, "argv", ["rosie", "--config", str(path), "start"])
    timer = threading.Timer(0.5, os.kill, (os.getpid(), signal.SIGINT))
    timer.start()
    cli.main()
    timer.join()


def test_start_without_the_robot_extra(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setitem(sys.modules, "rosie.process", None)  # as if numpy & co weren't installed
    monkeypatch.setattr(sys, "argv", ["rosie", "--config", str(tmp_path / "config.ini"), "start"])
    with pytest.raises(SystemExit) as stopped:
        cli.main()
    assert stopped.value.code == 1
    assert "pip install 'pyforce-rosie[robot]'" in capsys.readouterr().err
    assert not (tmp_path / "config.ini").exists()
