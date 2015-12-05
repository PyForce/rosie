# from robot.planner.maps.graph import AdjacencyMatrixGraph as Graph
import json


def generate(jsonfile):
    with open(jsonfile) as f:
        room_map = json.load(f)
    print(room_map)

generate('map.json')
