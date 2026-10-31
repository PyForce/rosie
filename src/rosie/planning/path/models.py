from dataclasses import dataclass

import numpy as np
from shapely.geometry import Polygon

type Points = np.ndarray  # n x 2: x, y in m


@dataclass(frozen=True, slots=True)
class Map:
    name: str
    border: Points  # outline of all the rooms together, first point not repeated
    obstacles: list[Points]  # outline of every item


@dataclass(frozen=True, slots=True)
class VisibilityGraph:
    vertices: Points
    adjacency: np.ndarray  # n x n, non-zero where two vertices see each other
    free_space: Polygon
    obstacles: list[Polygon]
