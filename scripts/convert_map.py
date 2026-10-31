"""
Convert a rosie 1 map (rooms with borders, walls, doors and items) into a rosie 2
map: a GeoJSON FeatureCollection with one feature per room, wall, door and obstacle.

    python scripts/convert_map.py my-house.json my-house.geojson

Only the standard library: it runs without rosie installed.
"""

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a rosie 1 map into a rosie 2 map.")
    parser.add_argument("old", type=Path, help="the rosie 1 map (.json)")
    parser.add_argument("new", type=Path, help="the rosie 2 map to write (.geojson)")
    args = parser.parse_args()
    collection = convert(json.loads(args.old.read_text()))
    features = ",\n".join(f"    {json.dumps(feature)}" for feature in collection["features"])
    args.new.write_text(
        "{\n"
        '  "type": "FeatureCollection",\n'
        f'  "name": {json.dumps(collection["name"])},\n'
        f'  "features": [\n{features}\n  ]\n'
        "}\n"
    )
    print(f"{args.new}: {len(collection['features'])} features")


def convert(old: dict[str, Any]) -> dict[str, Any]:
    """Rooms first, then walls, doors and obstacles, so they're drawn in that order."""
    rooms, walls, doors, obstacles = [], [], [], []
    for name, room in old["rooms"].items():
        rooms.append(_feature("room", room["borders"]["geometry"], {"name": name}))
        walls.append(_feature("wall", room["walls"]["geometry"], {"room": name}))
        doors.append(_feature("door", room["doors"]["geometry"], {"room": name}))
        obstacles += [
            _feature("obstacle", item["geometry"], {"name": item_name, "room": name})
            for item_name, item in room["items"].items()
            if item["geometry"]["coordinates"]
        ]
    features = rooms + walls + doors + obstacles
    return {"type": "FeatureCollection", "name": old["name"], "features": features}


def _feature(kind: str, geometry: dict[str, Any], properties: dict[str, str]) -> dict[str, Any]:
    coordinates = _positions(geometry["coordinates"])
    if geometry["type"] == "Polygon":
        # GeoJSON rings end on their first point
        coordinates = [ring if ring[0] == ring[-1] else [*ring, ring[0]] for ring in coordinates]
    return {
        "type": "Feature",
        "properties": {"kind": kind, **properties},
        "geometry": {"type": geometry["type"], "coordinates": coordinates},
    }


def _positions(coordinates: Any) -> Any:
    """Every position as (x, y): rosie 1 maps sometimes had a stray third value."""
    if coordinates and isinstance(coordinates[0], int | float):
        return [float(coordinates[0]), float(coordinates[1])]
    return [_positions(nested) for nested in coordinates]


if __name__ == "__main__":
    main()
