"""Path planning: the corners to drive through, around walls and furniture."""

import numpy as np
from shapely.geometry import Point
from shapely.ops import nearest_points

from rosie.planning.models import VisibilityGraph
from rosie.planning.search import astar_path
from rosie.planning.visibility import with_endpoints


def plan_path(
    graph: VisibilityGraph, start: tuple[float, float], goal: tuple[float, float]
) -> list[tuple[float, float]]:
    """
    The corners to drive through from `start` to `goal`, both included. A start outside
    the free space (the robot closer to a wall or furniture than the clearance) first
    goes straight to the nearest free point; a goal outside it has no route.
    """
    free_start, _ = nearest_points(graph.free_space, Point(start))
    escape = [] if free_start.equals(Point(start)) else [start]
    with_ends = with_endpoints(graph, np.array(free_start.coords[0]), np.array(goal))
    goal_index = len(with_ends.vertices) - 1
    path = astar_path(with_ends.vertices, with_ends.neighbors, goal_index - 1, goal_index)
    return [*escape, *((float(x), float(y)) for x, y in with_ends.vertices[path])]
