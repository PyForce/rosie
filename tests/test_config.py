from pathlib import Path

from rosie.config import DEFAULT_CONFIG, load_config


def test_writes_the_default_on_the_first_start(tmp_path: Path) -> None:
    path = tmp_path / "config.ini"
    config = load_config(path)
    assert path.read_text() == DEFAULT_CONFIG
    assert config.get("general", "profile") == "simubot"
    assert config.getboolean("web", "active")


def test_keeps_an_existing_config(tmp_path: Path) -> None:
    path = tmp_path / "config.ini"
    path.write_text("[general]\nprofile = kevin\nmap = 100%% mine\n")
    config = load_config(path)
    assert config.get("general", "profile") == "kevin"
    assert config.get("general", "map") == "100%% mine"  # no interpolation
