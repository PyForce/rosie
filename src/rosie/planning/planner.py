from pathlib import Path
from typing import Any

import numpy as np

from rosie.errors import NoRouteError
from rosie.planning.graph import astar_path
from rosie.planning.maps import load_map, read_map
from rosie.planning.models import Map, VisibilityGraph
from rosie.planning.visibility import visibility_graph, with_endpoints


class Planner:
    """Routes around the walls and furniture of the map in use."""

    def __init__(self, maps: dict[str, Path]) -> None:
        self.maps = maps
        self.world: Map | None = None
        self.map_name: str | None = None
        self._graph: VisibilityGraph | None = None
        self._clearance = 0.0

    def use_map(self, name: str) -> None:
        if name not in self.maps:
            raise ValueError(f"unknown map: {name}")
        self.world = load_map(self.maps[name])
        self.map_name = name
        self._graph = None

    def get_map(self, name: str) -> dict[str, Any] | None:
        return read_map(self.maps[name]) if name in self.maps else None

    def route(
        self, start: tuple[float, float], end: tuple[float, float], clearance: float
    ) -> list[tuple[float, float]]:
        """Corners to drive through from `start` to `end`, both included."""
        if self.world is None:
            raise NoRouteError("no map in use")
        if self._graph is None or self._clearance != clearance:
            self._graph = visibility_graph(self.world, clearance)
            self._clearance = clearance
        graph = with_endpoints(self._graph, np.array(start), np.array(end))
        path = astar_path(graph.vertices, graph.adjacency, np.array(start), np.array(end))
        return [(float(x), float(y)) for x, y in path]
