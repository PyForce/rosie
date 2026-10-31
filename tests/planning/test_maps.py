import json
from pathlib import Path

import pytest

from rosie.const import MAP
from rosie.planning.maps import MAPS_DIR, list_maps, load_map

HOUSE = MAP.default  # rosie's own map

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
    assert list(list_maps([tmp_path, MAPS_DIR])) == [HOUSE, "Garage"]
    write_map(tmp_path, HOUSE, {"Hall": room(0)})
    assert list_maps([tmp_path, MAPS_DIR])[HOUSE].parent == tmp_path


def test_rooms_must_form_one_floor(tmp_path: Path) -> None:
    path = write_map(tmp_path, "Islands", {"A": room(0), "B": room(5)})
    with pytest.raises(ValueError, match="don't form one connected floor"):
        load_map(path)
