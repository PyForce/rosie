from pathlib import Path

import pytest

from rosie.profile import PROFILES_DIR, load_profile


@pytest.mark.parametrize("profile_id", ["simubot", "kevin", "ltl", "rovert", "blubot"])
def test_builtin_profiles_load(profile_id: str) -> None:
    profile = load_profile(profile_id, [PROFILES_DIR])
    assert profile.id == profile_id
    assert profile.thumbnail.is_file()
    assert profile.vector.is_file()


def test_a_user_folder_comes_first(tmp_path: Path) -> None:
    mine = tmp_path / "simubot"
    mine.mkdir()
    (mine / "profile.toml").write_text(
        (PROFILES_DIR / "simubot" / "profile.toml")
        .read_text()
        .replace('name = "SIMUBOT"', 'name = "MINE"')
    )
    assert load_profile("simubot", [tmp_path, PROFILES_DIR]).name == "MINE"
    assert load_profile("kevin", [tmp_path, PROFILES_DIR]).directory == PROFILES_DIR / "kevin"


def test_unknown_profile(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown profile nobot"):
        load_profile("nobot", [tmp_path, PROFILES_DIR])


def test_incomplete_profile(tmp_path: Path) -> None:
    (tmp_path / "halfbot").mkdir()
    (tmp_path / "halfbot" / "profile.toml").write_text('name = "HALF"\nboard = "virtual"\n')
    with pytest.raises(ValueError, match="missing or unknown setting"):
        load_profile("halfbot", [tmp_path])
