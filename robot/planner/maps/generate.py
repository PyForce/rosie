# from robot.planner.maps.graph import AdjacencyMatrixGraph as Graph
import json
from collections import namedtuple

import matplotlib.pyplot as plt


H = 3
Point = namedtuple('Point', ['x', 'y', 'room'])
Vector = namedtuple('Vector', ['x', 'y'])
Rect = namedtuple('Rect', ['v', 'p0'])

def vector(A, B):
    return B[0] - A[0], B[1] - A[1]


def length(v):
    return (v[0] ** 2 + v[1] ** 2) ** 0.5


def norm(v):
    l = length(v)
    return v[0] / l, v[1] / l


def calculate_suport_points(points):
    for ps in points:
        n = len(ps)
        for i in range(n):
            # Three points for every step (two segments)
            xa, ya, r = ps[i]
            xb, yb, r = ps[(i + 1) % n]
            xc, yc, r = ps[(i + 2) % n]
            A = xa, ya
            B = xb, yb
            C = xc, yc

            v = norm(vector(A, B))
            w = norm(vector(B, C))

            # Rotate 90 grades
            _v = v[1], v[0]
            _w = w[1], w[0]

            _A = xa + _v[0], ya + _v[1]
            _B = xb + _w[0], yb + _w[1]

            r1 = Rect(vector(_A, _B), _A)


def get_all_points(rooms):
    points = [[]]
    for r in rooms.items():
        for ps in r[1]['borders']['geometry']['coordinates']:
            points[-1] += [Point(p[0], p[1], r[0]) for p in ps]
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
