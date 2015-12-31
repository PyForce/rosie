# from robot.planner.maps.graph import AdjacencyMatrixGraph as Graph
import json
from collections import namedtuple

import matplotlib.pyplot as plt


H = 3
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


def calculate_suport_points(points):
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

            v = norm(vector(A, B))
            w = norm(vector(B, C))

            # Rotate 90 grades
            _v = Vector(v.y, v.x)
            _w = Vector(w.y, w.x)

            _A = Point(xa + _v.x, ya + _v.y)
            _B = Point(xb + _w.x, yb + _w.y)

            r1 = Rect(vector(_A, _B), _A)


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

        #paint(allps)


generate('map.json')
