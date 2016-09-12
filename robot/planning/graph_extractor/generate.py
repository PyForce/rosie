# from robot.planner.maps.graph import AdjacencyMatrixGraph as Graph
import json
from collections import namedtuple

import numpy as np

import matplotlib.pyplot as plt

from map_tools import Map, get_all_points


H = 0.2
# RoomPoint = namedtuple('RoomPoint', ['x', 'y', 'room'])
# Point = namedtuple('Point', ['x', 'y'])

Vector = namedtuple('Vector', ['x', 'y'])
Rect = namedtuple('Rect', ['v', 'p0'])

Point = lambda x, y: np.array([x, y])
RoomPoint = lambda x, y, room: (np.array([x, y]), room)

def vector(A, B):
    return Vector(B.x - A.x, B.y - A.y)


def length(v):
    return (v.x ** 2 + v.y ** 2) ** 0.5


def norm(v):
    l = length(v)
    return Vector(v.x / l, v.y / l)

def point(r, p):
    pnt = Point(r.p0.x + r.v.x * p, r.p0.y + r.v.y * p)
    return Point(r.p0.x + r.v.x * p, r.p0.y + r.v.y * p)


def point_in_poly(point, polygon):
    """
    point = (x, y)
    polygon = [(x1, y1), ..., (xn, yn)]
    Asume the next segment is (xn, yn), (x0, y0)
    """
    x, y = point
    n = len(polygon)
    c = 0
    for i in range(n):
        inf = i
        sup = (i + 1) % n
        # Considering the y's order. Put inf down and sup up.
        if polygon[inf][1] > polygon[sup][1]:
            inf, sup = sup, inf
        (x_inf, y_inf), r = polygon[inf]
        (x_sup, y_sup), r = polygon[sup]
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


def compute_direction(poly):
    A, _ = poly[0]
    B, _ = poly[1]
    C, _ = poly[2]

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

    if point_in_poly(intersection(r1, r2), poly):
        return 1
    return -1


def get_suport_points(points):
    support_points = []
    for ps in points:
        try:
            direction = compute_direction(ps)
        except Exception as e:
            print(e)
            continue

        support_points.append([])
        n = len(ps)

        for i in range(n):
            # Three points for every step (two segments)
            A, _ = ps[direction * i]
            B, _ = ps[(direction * (i + 1)) % (direction * n)]
            C, _ = ps[(direction * (i + 2)) % (direction * n)]

            # Director vector of first rect
            v = B - A
            v /= np.linalg.norm(v)

            # Director vector of second rect
            w = C - B
            w /= np.linalg.norm(w)

            # Rotate 90 grades
            _v = Point(v[1], -v[0])
            _w = Point(w[1], -w[0])

            _A = A + H * _v
            _B = B + H * _w

            # plt.scatter(*_A)

            r1 = Rect(v, _A)
            r2 = Rect(w, _B)

            support_points[-1].append(intersection(r1, r2))
    return support_points


def get_walls(room):
    walls = []
    for coors in room['walls']['geometry']['coordinates']:
        walls.append(coors)
    return walls


def generate(jsonfile):

    m = Map(jsonfile)

    # Obtain a list which has for every room
    # the points of it's bounds
    all_points = get_all_points(m)

    suport_points = get_suport_points(all_points)
    #
    # print(suport_points)

    for wps in all_points:
        if wps: wps.append(wps[0])
        x = [p[0][0] for p in wps]
        y = [p[0][1] for p in wps]
        plt.plot(x, y)

    # walls = []
    # for room in rooms_map['rooms']:
    #     walls.extend(get_walls(rooms_map['rooms'][room]))

    # for wall in walls:
    #     x = [w[0] for w in wall]
    #     y = [w[1] for w in wall]
    #     plt.plot(x, y)

    # for wps in suport_points:
    #     if wps: wps.append(wps[0])
    #     x = [p[0] for p in wps]
    #     y = [p[1] for p in wps]
    #     plt.scatter(x, y)
        # plt.plot(x, y)

    plt.gca().axis('off')
    plt.gca().set_aspect(1)
    plt.xlim([-1, 9.2])
    plt.ylim([-1, 3.2])
    plt.show()


if __name__ == '__main__':
    from shapely.geometry import Polygon
    from descartes.patch import PolygonPatch

    m = Map('../maps/map.json')

    p = None

    for room in m.rooms:
        room_points = []
        for border in room.borders:
            room_points.extend(border)
        if room_points:
            p1 = Polygon(room_points)

        p = p1 if p is None else p.union(p1)

        x = [point[0] for point in room_points]
        y = [point[1] for point in room_points]
        plt.plot(x, y)

    patch = PolygonPatch(p)
    plt.gca().add_patch(patch)

    plt.gca().axis('off')
    plt.gca().set_aspect(1)
    plt.xlim([-1, 9.2])
    plt.ylim([-1, 3.2])
    plt.show()

    # generate('../maps/map.json')
