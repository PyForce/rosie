"""Path planning: the corners to drive through, around walls and furniture."""

import numpy as np

from rosie.planning.models import VisibilityGraph
from rosie.planning.search import astar_path
from rosie.planning.visibility import with_endpoints


def plan_path(
    graph: VisibilityGraph, start: tuple[float, float], goal: tuple[float, float]
) -> list[tuple[float, float]]:
    """The corners to drive through from `start` to `goal`, both included."""
    with_ends = with_endpoints(graph, np.array(start), np.array(goal))
    goal_index = len(with_ends.vertices) - 1
    path = astar_path(with_ends.vertices, with_ends.neighbors, goal_index - 1, goal_index)
    return [(float(x), float(y)) for x, y in with_ends.vertices[path]]
