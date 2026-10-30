"""
Visibility graph: the corners of the free space (the map shrunk by the robot's
clearance, its obstacles grown by it), linked when the robot can drive
straight from one to the other.
"""

from dataclasses import dataclass
from itertools import chain

import numpy as np
from shapely.geometry import JOIN_STYLE, LinearRing, LineString, Polygon

from rosie.planning.maps import Map, Points


@dataclass(frozen=True, slots=True)
class VisibilityGraph:
    vertices: Points
    adjacency: np.ndarray  # n x n, non-zero where two vertices see each other
    free_space: Polygon
    obstacles: list[Polygon]


def visibility_graph(world: Map, clearance: float) -> VisibilityGraph:
    border = _offset(world.border, clearance, "left", "right")
    holes = [
        _offset(obstacle, clearance, "right", "left")
        for obstacle in world.obstacles
        if obstacle.size > 0
    ]

    vertices = border
    for hole in holes:
        vertices = np.append(vertices, hole, axis=0)

    free_space = Polygon(border)
    obstacles = [Polygon(hole) for hole in holes]

    adjacency = np.zeros(shape=(len(vertices), len(vertices)))
    for i in range(vertices.shape[0]):
        for j in range(vertices.shape[0]):
            line = LineString(np.array((vertices[i], vertices[j])))
            if _is_free(line, free_space, obstacles):
                adjacency[i, j] = True
    return VisibilityGraph(vertices, adjacency, free_space, obstacles)


def with_endpoints(graph: VisibilityGraph, start: Points, end: Points) -> VisibilityGraph:
    """The graph plus `start` and `end` as its last two vertices."""
    vertices = np.append(graph.vertices, [start, end], axis=0)
    count = len(vertices) - 2
    adjacency = np.zeros(shape=(count + 2, count + 2))
    adjacency[:-2, :-2] = graph.adjacency
    for i in range(count):
        for j in range(count, count + 2):
            line = LineString(np.array((vertices[i], vertices[j])))
            if _is_free(line, graph.free_space, graph.obstacles):
                adjacency[i, j] = adjacency[j, i] = True
    return VisibilityGraph(vertices, adjacency, graph.free_space, graph.obstacles)


def _offset(outline: Points, clearance: float, side_if_ccw: str, side_if_cw: str) -> Points:
    closed = np.append(outline, [outline[0], outline[1]], axis=0)
    side = side_if_ccw if LinearRing(outline).is_ccw else side_if_cw
    # offset_curve goes left for positive distances, right for negative ones
    distance = clearance if side == "left" else -clearance
    offset = LineString(closed).offset_curve(distance, join_style=JOIN_STYLE.mitre)
    if offset.geom_type == "MultiLineString":
        first, second, *_ = offset.geoms
        return np.array(list(chain(first.coords, second.coords)))
    return np.array(list(offset.coords))


def _is_free(line: LineString, free_space: Polygon, obstacles: list[Polygon]) -> bool:
    for obstacle in obstacles:
        if obstacle.touches(line):
            continue
        if obstacle.intersects(line):
            return False
    return bool(free_space.contains(line))
