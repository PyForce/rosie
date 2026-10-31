"""
Maps: GeoJSON FeatureCollections (rosie's own in rosie/builtin/maps), with a
name and one feature per room, wall, door and obstacle (its "kind" property).
"""

import json
from pathlib import Path
from typing import Any

from shapely.geometry import LineString, MultiLineString, Polygon, shape
from shapely.ops import unary_union

from rosie.errors import SetupError
from rosie.world.models import World

BUILTIN_MAPS = Path(__file__).parents[1] / "builtin" / "maps"
DEFAULT_MAP = "Gustavo's House"
KINDS = ("room", "wall", "door", "obstacle")


def list_maps(search: list[Path]) -> dict[str, Path]:
    """Map name -> file, from every folder of `search` (the first one wins a name)."""
    maps: dict[str, Path] = {}
    for folder in reversed(search):
        maps |= {read_map(path)["name"]: path for path in sorted(folder.glob("*.geojson"))}
    return maps


def read_map(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text())
    return data


def load_world(path: Path) -> World:
    data = read_map(path)
    shapes: dict[str, list[Any]] = {kind: [] for kind in KINDS}
    try:
        for feature in data["features"]:
            kind = feature["properties"]["kind"]
            if kind not in shapes:
                raise SetupError(f"{path.name}: unknown kind {kind!r} (known: {', '.join(KINDS)})")
            shapes[kind].append(shape(feature["geometry"]))
    except (KeyError, TypeError) as error:
        raise SetupError(f"{path.name}: not a rosie map ({error})") from error
    floor = unary_union(shapes["room"])
    if not isinstance(floor, Polygon):
        raise SetupError(f"the rooms of {path.name} don't form one connected floor")
    walls = [
        line
        for wall in shapes["wall"]
        for line in (wall.geoms if isinstance(wall, MultiLineString) else [wall])
        if isinstance(line, LineString)
    ]
    return World(data["name"], floor, tuple(walls), tuple(shapes["obstacle"]))
