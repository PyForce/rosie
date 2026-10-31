"""
Visibility graph: the corners of the free space (the floor shrunk by the robot's
clearance, minus its walls and obstacles grown by it), linked when the robot can
drive straight from one to the other.
"""

from collections.abc import Iterable

import numpy as np
from shapely.geometry import LineString, MultiPolygon, Polygon
from shapely.ops import unary_union

from rosie.errors import NoRouteError
from rosie.planning.models import VisibilityGraph
from rosie.world.models import Points, World


def visibility_graph(world: World, clearance: float) -> VisibilityGraph:
    floor = world.floor.buffer(-clearance, join_style="mitre")
    grown = [item.buffer(clearance, join_style="mitre") for item in world.obstacles]
    # square caps: the robot keeps its clearance from a wall's ends too, at the doors
    grown += [
        wall.buffer(clearance, cap_style="square", join_style="mitre") for wall in world.walls
    ]
    free_space = floor.difference(unary_union(grown))
    if not isinstance(free_space, Polygon | MultiPolygon) or free_space.is_empty:
        raise NoRouteError(f"no free space on {world.name} with a clearance of {clearance:.2f} m")
    vertices = _corners(free_space)
    return VisibilityGraph(
        free_space, vertices, _neighbors(free_space, vertices, range(len(vertices)))
    )


def with_endpoints(graph: VisibilityGraph, start: Points, goal: Points) -> VisibilityGraph:
    """The graph plus `start` and `goal` as its last two vertices, linked to what they see."""
    vertices = np.append(graph.vertices, [start, goal], axis=0)
    new = (len(vertices) - 2, len(vertices) - 1)
    seen_from_new = dict(zip(new, _neighbors(graph.free_space, vertices, new), strict=True))
    old = tuple(
        (*seen, *(index for index in new if i in seen_from_new[index]))
        for i, seen in enumerate(graph.neighbors)
    )
    return VisibilityGraph(graph.free_space, vertices, (*old, *seen_from_new.values()))


def _neighbors(
    free_space: Polygon | MultiPolygon, vertices: Points, of: Iterable[int]
) -> tuple[tuple[int, ...], ...]:
    """For each vertex in `of`, the vertices it sees."""
    return tuple(
        tuple(
            j
            for j in range(len(vertices))
            if j != i and _sees(free_space, vertices[i], vertices[j])
        )
        for i in of
    )


def _corners(free_space: Polygon | MultiPolygon) -> Points:
    polygons = free_space.geoms if isinstance(free_space, MultiPolygon) else [free_space]
    rings = [ring for polygon in polygons for ring in (polygon.exterior, *polygon.interiors)]
    # each ring repeats its first point at the end
    return np.array([point for ring in rings for point in ring.coords[:-1]])


def _sees(free_space: Polygon | MultiPolygon, a: Points, b: Points) -> bool:
    return bool(free_space.covers(LineString([a, b])))
