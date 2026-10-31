import json
from pathlib import Path

import pytest

from rosie.planning.maps import BUILTIN_MAPS, DEFAULT_MAP, list_maps, load_map

SQUARE = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]


def room(offset: float) -> dict[str, object]:
    square = [[x + offset, y] for x, y in SQUARE]
    return {
        "borders": {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [square]}},
        "items": {},
    }


def write_map(folder: Path, name: str, rooms: dict[str, object]) -> Path:
    path = folder / f"{name.lower()}.json"
    path.write_text(json.dumps({"name": name, "rooms": rooms}))
    return path


def test_user_maps_join_and_override_the_builtin_ones(tmp_path: Path) -> None:
    write_map(tmp_path, "Garage", {"Garage": room(0)})
    assert list(list_maps([tmp_path, BUILTIN_MAPS])) == [DEFAULT_MAP, "Garage"]
    write_map(tmp_path, DEFAULT_MAP, {"Hall": room(0)})
    assert list_maps([tmp_path, BUILTIN_MAPS])[DEFAULT_MAP].parent == tmp_path


def test_rooms_must_form_one_floor(tmp_path: Path) -> None:
    path = write_map(tmp_path, "Islands", {"A": room(0), "B": room(5)})
    with pytest.raises(ValueError, match="don't form one connected floor"):
        load_map(path)
