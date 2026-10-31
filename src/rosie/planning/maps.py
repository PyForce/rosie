"""
Floor maps (JSON files, rosie's own in rosie/builtin/maps): rooms with their borders, and the
items (furniture) in them.
"""

import json
from pathlib import Path
from typing import Any

import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

from rosie.errors import SetupError
from rosie.planning.models import Map, Points

BUILTIN_MAPS = Path(__file__).parent.parent / "builtin" / "maps"
DEFAULT_MAP = "Gustavo's House"


def list_maps(search: list[Path]) -> dict[str, Path]:
    """Map name -> file, from every folder of `search` (the first one wins a name)."""
    maps: dict[str, Path] = {}
    for folder in reversed(search):
        maps |= {read_map(path)["name"]: path for path in sorted(folder.glob("*.json"))}
    return maps


def read_map(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text())
    return data


def load_map(path: Path) -> Map:
    data = read_map(path)
    rooms = data["rooms"].values()
    union = unary_union([Polygon(_room_border(room)) for room in rooms])
    if not isinstance(union, Polygon):
        raise SetupError(f"the rooms of {path.name} don't form one connected floor")
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
