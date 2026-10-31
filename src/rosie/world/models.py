from dataclasses import dataclass

import numpy as np
from shapely.geometry import LineString, Polygon

type Points = np.ndarray  # n x 2: x, y in m


@dataclass(frozen=True, slots=True)
class World:
    """The environment the robot moves in, from a map file."""

    name: str
    floor: Polygon  # all the rooms together
    walls: tuple[LineString, ...]  # the gaps between them are the doors
    obstacles: tuple[Polygon, ...]  # furniture
