import json
from pathlib import Path

import pytest
from shapely.geometry import Polygon

from rosie.world.maps import BUILTIN_MAPS, DEFAULT_MAP, list_maps, load_world

SQUARE = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]


def room(name: str, offset: float) -> dict[str, object]:
    square = [[x + offset, y] for x, y in SQUARE]
    return {
        "type": "Feature",
        "properties": {"kind": "room", "name": name},
        "geometry": {"type": "Polygon", "coordinates": [square]},
    }


def write_map(folder: Path, name: str, features: list[dict[str, object]]) -> Path:
    path = folder / f"{name.lower()}.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "name": name, "features": features}))
    return path


def test_the_house() -> None:
    house = load_world(list_maps([BUILTIN_MAPS])[DEFAULT_MAP])
    assert house.name == DEFAULT_MAP
    assert isinstance(house.floor, Polygon)
    assert (len(house.walls), len(house.obstacles)) == (8, 5)


def test_user_maps_join_and_override_the_builtin_ones(tmp_path: Path) -> None:
    write_map(tmp_path, "Garage", [room("Garage", 0)])
    assert list(list_maps([tmp_path, BUILTIN_MAPS])) == [DEFAULT_MAP, "Garage"]
    write_map(tmp_path, DEFAULT_MAP, [room("Hall", 0)])
    assert list_maps([tmp_path, BUILTIN_MAPS])[DEFAULT_MAP].parent == tmp_path


def test_rooms_must_form_one_floor(tmp_path: Path) -> None:
    path = write_map(tmp_path, "Islands", [room("A", 0), room("B", 5)])
    with pytest.raises(ValueError, match="don't form one connected floor"):
        load_world(path)


def test_an_unknown_kind(tmp_path: Path) -> None:
    lamp = {**room("Lamp", 0), "properties": {"kind": "lamp"}}
    with pytest.raises(ValueError, match="unknown kind 'lamp'"):
        load_world(write_map(tmp_path, "Lamps", [room("A", 0), lamp]))


def test_not_a_rosie_map(tmp_path: Path) -> None:
    path = tmp_path / "old.geojson"
    path.write_text(json.dumps({"name": "Old", "rooms": {}}))
    with pytest.raises(ValueError, match=r"old\.geojson: not a rosie map"):
        load_world(path)


def test_a_wall_must_be_a_line(tmp_path: Path) -> None:
    wall = {**room("Wall", 0), "properties": {"kind": "wall"}}  # a polygon
    with pytest.raises(
        ValueError, match="a wall is a LineString or MultiLineString, not a Polygon"
    ):
        load_world(write_map(tmp_path, "Thick walls", [room("A", 0), wall]))


def test_several_obstacles_in_one_feature(tmp_path: Path) -> None:
    chairs: dict[str, object] = {
        "type": "Feature",
        "properties": {"kind": "obstacle", "name": "chairs"},
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0.1, 0.1], [0.2, 0.1], [0.2, 0.2], [0.1, 0.1]]],
                [[[0.6, 0.6], [0.7, 0.6], [0.7, 0.7], [0.6, 0.6]]],
            ],
        },
    }
    world = load_world(write_map(tmp_path, "Chairs", [room("A", 0), chairs]))
    assert len(world.obstacles) == 2
