from pathlib import Path

import pytest

from rosie.profile import BUILTIN_PROFILES, load_profile


@pytest.mark.parametrize("profile_id", ["simubot", "kevin", "ltl", "rovert", "blubot"])
def test_builtin_profiles_load(profile_id: str) -> None:
    profile = load_profile(profile_id)
    assert profile.id == profile_id
    assert profile.thumbnail.is_file()
    assert profile.vector.is_file()
    assert profile.sensors == {}


def copy_of_simubot(folder: Path, extra: str = "") -> Path:
    folder.mkdir()
    text = (BUILTIN_PROFILES / "simubot" / "profile.toml").read_text()
    (folder / "profile.toml").write_text(text.replace('name = "SIMUBOT"', 'name = "MINE"') + extra)
    return folder


def test_your_robot_by_its_folder(tmp_path: Path) -> None:
    profile = load_profile(str(copy_of_simubot(tmp_path / "my-robot")))
    assert (profile.id, profile.name) == ("my-robot", "MINE")
    assert profile.maps == tmp_path / "my-robot" / "maps"


def test_a_folder_named_like_a_builtin_robot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copy_of_simubot(tmp_path / "simubot")
    monkeypatch.chdir(tmp_path)
    assert load_profile("simubot").name == "SIMUBOT"  # a name is rosie's own
    assert load_profile("./simubot").name == "MINE"  # a path is yours


def test_sensors(tmp_path: Path) -> None:
    folder = copy_of_simubot(tmp_path / "sonarbot", "\n[sensors.usound]\naddress = 0x11\n")
    assert load_profile(str(folder)).sensors == {"usound": {"address": 0x11}}


def test_unknown_profile(tmp_path: Path) -> None:
    with pytest.raises(
        ValueError, match=r"unknown robot profile nobot: .*rosie's own: blubot, kevin"
    ):
        load_profile("nobot")
    with pytest.raises(ValueError, match="unknown robot"):
        load_profile(str(tmp_path))


def test_incomplete_profile(tmp_path: Path) -> None:
    (tmp_path / "profile.toml").write_text('name = "HALF"\n[board]\ntype = "virtual"\n')
    with pytest.raises(ValueError, match="missing or unknown setting"):
        load_profile(str(tmp_path))


def test_a_profile_from_rosie_1(tmp_path: Path) -> None:
    (tmp_path / "profile.toml").write_text('name = "OLD"\nboard = "virtual"\n')
    with pytest.raises(ValueError, match=r"needs a \[board\] table"):
        load_profile(str(tmp_path))
