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
    path = astar_path(with_ends.vertices, with_ends.adjacency, np.array(start), np.array(goal))
    return [(float(x), float(y)) for x, y in path]
