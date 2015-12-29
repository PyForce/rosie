# from robot.planner.maps.graph import AdjacencyMatrixGraph as Graph
import json
from collections import namedtuple


Point = namedtuple('Point', ['x', 'y', 'room'])

def get_all_wall_points(rooms):
    points = []
    for r in rooms.items():
        for ps in r[1]['walls']['geometry']['coordinates']:
            for p in ps:
                points.append(Point(p[0], p[1], r[0]))
    return points


def generate(jsonfile):
    rooms_map = None
    with open(jsonfile) as f:
        rooms_map = json.load(f)
    if rooms_map:
        allwps = get_all_wall_points(rooms_map['rooms'])
        print(allwps)

generate('map.json')
