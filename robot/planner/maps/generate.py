# from robot.planner.maps.graph import AdjacencyMatrixGraph as Graph
import json
from collections import namedtuple
import numpy as np

import matplotlib.pyplot as plt


H = 0.2
RoomPoint = namedtuple('RoomPoint', ['x', 'y', 'room'])
Point = namedtuple('Point', ['x', 'y'])
Vector = namedtuple('Vector', ['x', 'y'])
Rect = namedtuple('Rect', ['v', 'p0'])

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

def intersection(r1, r2):
    """
    (x01, y01) = r1.p0
    (a1, b1)   = r1.v

    (x02, y02) = r2.p0
    (a2, b2)   = r2.v
    """

    x01, y01 = r1.p0
    a1, b1   = r1.v

    x02, y02 = r2.p0
    a2, b2   = r2.v

    c1, c2 = x02 - x01, y02 - y01

    A = np.matrix([[a1, a2], [b1, b2]])
    b = np.matrix([[c1, c2]]).T
    x = np.linalg.solve(A, b)

    return Point(x01 + x[0,0] * a1, y01 + x[0,0] * b1)


def calculate_suport_points(points):
    sps = [[]]
    for ps in points:
        n = len(ps)
        for i in range(n):
            # Three points for every step (two segments)
            xa, ya, r = ps[i]
            xb, yb, r = ps[(i + 1) % n]
            xc, yc, r = ps[(i + 2) % n]

            # Convert to real points
            A = Point(xa, ya)
            B = Point(xb, yb)
            C = Point(xc, yc)

            # Director vector of first rect
            v = norm(vector(A, B))
            # Director vector of second rect
            w = norm(vector(B, C))

            # Rotate -90 grades
            _v = Vector(v.y, -v.x)
            _w = Vector(w.y, -w.x)

            _A = Point(xa + H * _v.x, ya + H * _v.y)
            _B = Point(xb + H * _w.x, yb + H * _w.y)

            r1 = Rect(v, _A)
            r2 = Rect(w, _B)

            sps[-1].append(intersection(r1, r2))
        sps.append([])
    return sps


def get_all_points(rooms):
    points = [[]]
    for r in rooms.items():
        for ps in r[1]['borders']['geometry']['coordinates']:
            points[-1] += [RoomPoint(p[0], p[1], r[0]) for p in ps]
        points.append([])
    return points


def paint(allps):
    for wps in allps:
        x = [p.x for p in wps]
        y = [p.y for p in wps]
        plt.plot(x, y)
    plt.xlim([-1, 9.2])
    plt.ylim([-1, 3.2])
    plt.show()

def generate(jsonfile):
    rooms_map = None
    with open(jsonfile) as f:
        rooms_map = json.load(f)
    if rooms_map:
        # Obtain a list which has for every room
        # the points of it's bounds
        allps = get_all_points(rooms_map['rooms'])
        sallps = calculate_suport_points(allps)

        for wps in allps:
            x = [p.x for p in wps]
            y = [p.y for p in wps]
            plt.plot(x, y)

        for wps in sallps:
            x = [p.x for p in wps]
            y = [p.y for p in wps]
            plt.scatter(x, y)
        plt.xlim([-1, 9.2])
        plt.ylim([-1, 3.2])
        plt.show()


generate('map.json')
