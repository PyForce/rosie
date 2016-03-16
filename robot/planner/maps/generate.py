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
        x_inf, y_inf, r = polygon[inf]
        x_sup, y_sup, r = polygon[sup]
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

    x01, y01 = r1.p0
    a1, b1   = r1.v

    x02, y02 = r2.p0
    a2, b2   = r2.v

    c1, c2 = x02 - x01, y02 - y01

    A = np.matrix([[a1, a2], [b1, b2]])
    b = np.matrix([[c1, c2]]).T
    x = np.linalg.solve(A, b)

    return Point(x01 + x[0,0] * a1, y01 + x[0,0] * b1)


def compute_direction(ps):
    xa, ya, r = ps[0]
    xb, yb, r = ps[1]
    xc, yc, r = ps[2]

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

    if point_in_poly(intersection(r1, r2), ps):
        return 1
    return -1


def calculate_suport_points(points):
    sps = []
    for ps in points:
        try:
            direction = compute_direction(ps)
        except:
            continue

        sps.append([])
        n = len(ps)

        for i in range(n):
            # Three points for every step (two segments)
            xa, ya, r = ps[direction * i]
            xb, yb, r = ps[(direction * (i + 1)) % (direction * n)]
            xc, yc, r = ps[(direction * (i + 2)) % (direction * n)]

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

def get_walls(room):
    walls = []
    for coors in room['walls']['geometry']['coordinates']:
        walls.append(coors)
    return walls

def generate(jsonfile):
    rooms_map = None
    with open(jsonfile) as f:
        rooms_map = json.load(f)
    if rooms_map:
        # Obtain a list which has for every room
        # the points of it's bounds
        allps = get_all_points(rooms_map['rooms'])
        sallps = calculate_suport_points(allps)

        # for wps in allps:
        #     # if wps: wps.append(wps[0])
        #     x = [p.x for p in wps]
        #     y = [p.y for p in wps]
        #     plt.plot(x, y)

        walls = []
        for room in rooms_map['rooms']:
            walls.extend(get_walls(rooms_map['rooms'][room]))

        for wall in walls:
            x = [w[0] for w in wall]
            y = [w[1] for w in wall]
            plt.plot(x, y)

        for wps in sallps:
            if wps: wps.append(wps[0])
            x = [p.x for p in wps]
            y = [p.y for p in wps]
            plt.scatter(x, y)
            plt.plot(x, y)

        plt.gca().axis('off')
        plt.gca().set_aspect(1)
        plt.xlim([-1, 9.2])
        plt.ylim([-1, 3.2])
        plt.show()

generate('map.json')
