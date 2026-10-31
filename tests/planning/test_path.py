import math
from itertools import pairwise

import pytest
from shapely.geometry import LineString, Polygon

from rosie.errors import NoRouteError
from rosie.planning.path import plan_path
from rosie.planning.visibility import visibility_graph
from rosie.world.models import World

# a 4 m x 4 m room with a 1 m box in the middle
ROOM = World(
    name="Box room",
    floor=Polygon([(0, 0), (4, 0), (4, 4), (0, 4)]),
    walls=(),
    obstacles=(Polygon([(1.5, 1.5), (2.5, 1.5), (2.5, 2.5), (1.5, 2.5)]),),
)


def length(route: list[tuple[float, float]]) -> float:
    return sum(math.dist(a, b) for a, b in pairwise(route))


def test_a_target_in_sight_is_a_straight_line() -> None:
    graph = visibility_graph(ROOM, 0.2)
    assert plan_path(graph, (0.5, 0.5), (3.5, 0.5)) == [(0.5, 0.5), (3.5, 0.5)]


def test_it_goes_around_an_obstacle_by_its_grown_corners() -> None:
    graph = visibility_graph(ROOM, 0.2)
    route = plan_path(graph, (0.5, 2.0), (3.5, 2.0))
    assert len(route) == 4  # start, two corners of the grown box, target
    # along one side of the box (both are as short): 0.5 m from the middle, plus the clearance
    assert abs(route[1][1] - 2.0) == abs(route[2][1] - 2.0) == pytest.approx(0.7)
    assert length(route) < 3.0 + 2 * 1.4  # shorter than the far way round


def test_a_clearance_bigger_than_the_room() -> None:
    with pytest.raises(NoRouteError, match="no free space on Box room"):
        visibility_graph(ROOM, 2.5)


def test_a_start_too_close_to_the_walls_first_gets_away_from_them() -> None:
    graph = visibility_graph(ROOM, 0.2)
    # the robot in the room's corner: to the nearest free point, then on
    assert plan_path(graph, (0.0, 0.0), (3.5, 0.5)) == [(0.0, 0.0), (0.2, 0.2), (3.5, 0.5)]


def test_a_target_inside_an_obstacle() -> None:
    graph = visibility_graph(ROOM, 0.2)
    with pytest.raises(NoRouteError, match=r"no route from \(0.50, 0.50\) to \(2.00, 2.00\)"):
        plan_path(graph, (0.5, 0.5), (2.0, 2.0))


def test_walls_make_the_robot_use_the_door() -> None:
    # two 2 m x 2 m rooms side by side; the wall between them leaves a door at the bottom
    two_rooms = World(
        name="Two rooms",
        floor=Polygon([(0, 0), (4, 0), (4, 2), (0, 2)]),
        walls=(LineString([(2, 0.8), (2, 2)]),),
        obstacles=(),
    )
    route = plan_path(visibility_graph(two_rooms, 0.1), (1.0, 1.5), (3.0, 1.5))
    assert len(route) > 2  # not the straight line through the wall
    assert all(y < 0.8 for _, y in route[1:-1])  # through the door
