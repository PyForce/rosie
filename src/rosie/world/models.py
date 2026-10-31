from dataclasses import dataclass

import numpy as np

type Points = np.ndarray  # n x 2: x, y in m


@dataclass(frozen=True, slots=True)
class World:
    """The environment the robot moves in, from a map file."""

    name: str
    border: Points  # outline of all the rooms together, first point not repeated
    obstacles: list[Points]  # outline of every item
