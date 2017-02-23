from __future__ import print_function
from os.path import abspath, dirname, join as joinpath

# from robot.planner.maps.graph import AdjacencyMatrixGraph as Graph
import json
from collections import namedtuple

import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

from map_tools import Map


H = 0.2
Rect = namedtuple('Rect', ['v', 'p0'])
Point = lambda x, y: np.array([x, y])


def point_in_poly(point, polygon):
    """
    point = (x, y)
    polygon = [(x1, y1), ..., (xn, yn)]
    Asume the next segment is (xn, yn), (x0, y0)
    """
    x, y = point
    n = polygon.shape[0]
    c = 0
    for i in range(n):
        inf = i
        sup = (i + 1) % n
        # Considering the y's order. Put inf down and sup up.
        if polygon[inf, 1] > polygon[sup, 1]:
            inf, sup = sup, inf
        x_inf, y_inf = polygon[inf, :].T
        x_sup, y_sup = polygon[sup, :].T
        # The y in inf must be less or equal than the y of the point and.
        # the y in sup must be greate than the y of the point.
        # Considering the y order, the point must be in the midle of
        # inf and sup.
        if y_inf <= y < y_sup:
            # A is the vector Inf - P
            A_x, A_y = x - x_inf, y - y_inf
            # B is the vector Inf - Sup
            B_x, B_y = x_sup - x_inf, y_sup - y_inf
            # The movement must antihorary
            if A_x * B_y > A_y * B_x:
                c += 1
    return c % 2 == 1


def intersection(r1, r2):
    """
    (x01, y01) = r1.p0
    (a1, b1)   = r1.v

    (x02, y02) = r2.p0
    (a2, b2)   = r2.v
    """

    v1, p1 = r1

    v2, p2 = r2

    c1, c2 = p2 - p1

    A = np.matrix([v1, -v2]).T
    b = np.matrix([[c1, c2]]).T
    x = np.linalg.solve(A, b)

    return p1 + x[0,0] * v1


def compute_direction(points):
    A = points[0, :]
    B = points[1, :]
    C = points[2, :]

    A, B, C = map(lambda P: np.array(P).reshape(2), [A, B, C])

    # Director vector of first rect
    v = B - A
    v /= np.linalg.norm(v)

    # Director vector of second rect
    w = C - A
    w /= np.linalg.norm(w)

    # Rotate 90 grades
    _v = Point(v[1], -v[0])
    _w = Point(w[1], -w[0])

    _A = A + H * _v
    _B = B + H * _w

    r1 = Rect(v, _A)
    r2 = Rect(w, _B)

    if point_in_poly(intersection(r1, r2), points):
        return 1
    return -1


def get_suport_points(points):
    support_points = []
    n = points.shape[0]

    direction = 1

    if points.shape[0] < 3:
        return None
    # Check witch is the directions of the polygon
    direction = compute_direction(points)

    for i in range(n):
        # Three points for every step (two segments)
        A = points[direction * i, :]
        B = points[(direction * (i + 1)) % (direction * n), :]
        C = points[(direction * (i + 2)) % (direction * n), :]

        A, B, C = map(lambda P: np.array(P).reshape(2), [A, B, C])

        # Director vector of first rect
        v = B - A
        v /= np.linalg.norm(v)
        # Director vector of second rect
        w = C - B
        w /= np.linalg.norm(w)

        if np.isclose(np.abs(v.dot(w)), 1):
            continue

        # Rotate 90 grades
        _v = Point(v[1], -v[0])
        _w = Point(w[1], -w[0])

        _A = A + H * _v
        _B = B + H * _w

        r1 = Rect(v, _A)
        r2 = Rect(w, _B)

        support_points.append(intersection(r1, r2))
    return support_points


def get_walls(room):
    walls = []
    for coors in room['walls']['geometry']['coordinates']:
        walls.append(coors)
    return walls


def generate(jsonfile):
    m = Map(jsonfile)

    # Get the complete polygon of the union of all rooms
    p = None
    for room in m.rooms:
        p1 = Polygon(room.borders_points)
        p = p1 if p is None else p.union(p1)

    points = list(p.exterior.coords)
    if points:
        filtered_points = [points[0]]
        for i in range(1, len(points) - 1):
            if points[i][0] == filtered_points[-1][0] and points[i][1] == filtered_points[-1][1]:
                continue
            else:
                filtered_points.append(points[i])

    all_points = np.matrix(filtered_points)
    suport_points = get_suport_points(all_points)

    # suport_points = [[s[0], s[1]] for s in suport_points]
    # print(suport_points)

    lines = [[i, (i+1) % len(suport_points)] for i in range(len(suport_points))]
    points = [[s[0], s[1]] for s in suport_points]

    from find_graph import find_graph
    vg = find_graph(points, lines, [[0, 0, [-np.Inf, -np.Inf, np.Inf, np.Inf]]])

    # Plot test
    x, y = all_points[:, 0], all_points[:, 1]
    plt.plot(x, y)

    suport_points = np.matrix(suport_points)

    x, y = suport_points[:, 0], suport_points[:, 1]
    plt.scatter(x, y)
    plt.plot(x, y, 'b')

    for i in range(vg.shape[0]):
        for j in range(vg.shape[1]):
            if vg[i, j]:
                x = suport_points[i, 0], suport_points[j, 0]
                y = suport_points[i, 1], suport_points[j, 1]
                plt.plot(x, y, 'r')

    plt.gca().axis('off')
    plt.gca().set_aspect(1)
    plt.show()


if __name__ == '__main__':
    path = abspath(joinpath(dirname(__file__), '..', 'maps', 'map.json'))
    generate(path)
