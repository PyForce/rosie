from heapq import heappop, heappush
from itertools import count

import numpy as np

from rosie.errors import NoRouteError
from rosie.world.models import Points


def astar_path(
    vertices: Points, adjacency: np.ndarray, source: Points, target: Points
) -> list[Points]:
    """Shortest path between two of the vertices (A*, after NetworkX's)."""
    source_index = _index_of(vertices, source)
    tie_breaker = count()
    queue = [(0.0, next(tie_breaker), source_index, 0.0, -1)]
    enqueued: dict[int, tuple[float, float]] = {}
    explored: dict[int, int] = {}

    while queue:
        _, _, u, path_dist, parent = heappop(queue)
        vertex = vertices[u]
        if all(vertex == target):
            return _path(vertices, explored, u, parent)

        if u in explored:
            continue

        explored[u] = parent

        for v in _neighbors(adjacency, u):
            neighbor = vertices[v]
            if v in explored:
                continue
            ncost = path_dist + _distance(vertex, neighbor)
            if v in enqueued:
                qcost, h = enqueued[v]
                if qcost <= ncost:
                    continue
            else:
                h = _distance(neighbor, target)
            enqueued[v] = ncost, h
            heappush(queue, (ncost + h, next(tie_breaker), v, ncost, u))

    raise NoRouteError(f"no route from {_point(source)} to {_point(target)}: target not found")


def _index_of(vertices: Points, source: Points) -> int:
    for index, vertex in enumerate(vertices):
        if all(source == vertex):
            return index
    raise NoRouteError(f"the start {_point(source)} is not in the graph")


def _path(vertices: Points, explored: dict[int, int], end: int, parent: int) -> list[Points]:
    path = [vertices[end]]
    node = parent
    while node != -1:
        path.append(vertices[node])
        node = explored[node]
    path.reverse()
    return path


def _neighbors(adjacency: np.ndarray, u: int) -> list[int]:
    return [v for v in range(len(adjacency)) if adjacency[u, v]]


def _distance(a: Points, b: Points) -> float:
    x, y = a - b
    return float(np.hypot(x, y))


def _point(point: Points) -> str:
    x, y = point
    return f"({x:.2f}, {y:.2f})"
