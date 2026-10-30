"""
Floor maps (JSON files in rosie/maps): rooms with their borders, and the
items (furniture) in them.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

MAPS_DIR = Path(__file__).parent.parent / "maps"

type Points = np.ndarray  # n x 2: x, y in m


@dataclass(frozen=True, slots=True)
class Map:
    name: str
    border: Points  # outline of all the rooms together, first point not repeated
    obstacles: list[Points]  # outline of every item


def list_maps() -> dict[str, Path]:
    return {read_map(path)["name"]: path for path in sorted(MAPS_DIR.iterdir())}


def read_map(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text())
    return data


def load_map(path: Path) -> Map:
    data = read_map(path)
    rooms = data["rooms"].values()
    union = unary_union([Polygon(_room_border(room)) for room in rooms])
    if not isinstance(union, Polygon):
        raise ValueError(f"the rooms of {path.name} don't form one connected floor")
    obstacles = [
        np.array(item["geometry"]["coordinates"][0])
        for room in rooms
        for item in room["items"].values()
        if item["geometry"]["coordinates"]
    ]
    return Map(data["name"], np.array(union.exterior.coords)[:-1], obstacles)


def _room_border(room: dict[str, Any]) -> Points:
    rings = room["borders"]["geometry"]["coordinates"]
    return np.array([(x, y) for ring in rings for x, y in ring])
