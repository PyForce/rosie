"""A* on a graph whose vertices are points: the cost of an edge is its length."""

import math
from heapq import heappop, heappush

from rosie.errors import NoRouteError
from rosie.world.models import Points


def astar_path(
    vertices: Points, neighbors: tuple[tuple[int, ...], ...], source: int, target: int
) -> list[int]:
    """The shortest path from `source` to `target`, as vertex indices, both included."""
    goal = vertices[target]
    cost = {source: 0.0}
    came_from: dict[int, int] = {}
    frontier = [(_distance(vertices[source], goal), source)]
    done: set[int] = set()
    while frontier:
        _, vertex = heappop(frontier)
        if vertex == target:
            return _walk_back(came_from, source, target)
        if vertex in done:
            continue
        done.add(vertex)
        for neighbor in neighbors[vertex]:
            new_cost = cost[vertex] + _distance(vertices[vertex], vertices[neighbor])
            if new_cost < cost.get(neighbor, math.inf):
                cost[neighbor] = new_cost
                came_from[neighbor] = vertex
                heappush(frontier, (new_cost + _distance(vertices[neighbor], goal), neighbor))
    raise NoRouteError(f"no route from {_point(vertices[source])} to {_point(goal)}")


def _walk_back(came_from: dict[int, int], source: int, target: int) -> list[int]:
    path = [target]
    while path[-1] != source:
        path.append(came_from[path[-1]])
    return path[::-1]


def _distance(a: Points, b: Points) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _point(point: Points) -> str:
    return f"({point[0]:.2f}, {point[1]:.2f})"
