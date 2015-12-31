# from robot.planner.maps.graph import AdjacencyMatrixGraph as Graph
import json
from collections import namedtuple

import matplotlib.pyplot as plt


Point = namedtuple('Point', ['x', 'y', 'room'])

def calculate_suport_points(points):
    for ps in points:
        pass


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

        paint(allps)


generate('map.json')
