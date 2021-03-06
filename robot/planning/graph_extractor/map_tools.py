"""
Map tools
"""
from __future__ import print_function

import json
import os
from itertools import chain

import numpy as np
from shapely.geometry import JOIN_STYLE, LinearRing, LineString, Polygon
from shapely.ops import cascaded_union


def _get_all_features(item):
    item_type = item['type']
    item_geometry = item['geometry']
    item_geometry_type = item_geometry['type']
    item_geometry_coordinates = item_geometry['coordinates']
    return item_type, item_geometry, item_geometry_type, item_geometry_coordinates


def _get_any(item, item_name, expected='', func=lambda l: sum(l, [])):
    item = item[item_name]
    _, _, geometry_type, coordinates = _get_all_features(item)
    if expected:
        assert geometry_type == expected, item_name + ' accesor in a not ' + expected + ' Item'
    return func(coordinates)


def _get_borders(item, func=lambda l: sum(l, [])):
    """
    Get the borders coordinates then apply the function `func`
    """
    return _get_any(item, 'borders', 'Polygon', func)


def _get_walls(item, func=lambda l: sum(l, [])):
    return _get_any(item, 'walls', 'MultiLineString', func)


def _get_doors(item, func=lambda l: sum(l, [])):
    return _get_any(item, 'doors', 'MultiLineString', func)


def _get_all_items(item, func=lambda l: sum(l, [])):
    return {item_name: _get_any(item_val, item_name, 'Polygon', func)
            for item_name, item_val in item.items()}


def list_maps(mapdir='../maps'):
    """
    Lazy return all maps in `mapdir` directory
    """
    mapdir = os.path.join(os.path.dirname(__file__), mapdir)
    for tmap in os.listdir(mapdir):
        map_path = os.path.abspath(os.path.join(mapdir, tmap))
        with open(map_path, 'r') as map_file:
            yield map_path, json.load(map_file)


class Item(object):
    """
    Abstraction structure for Items
    """
    def __init__(self, item, item_name='', locations=None, parent_item=None):
        self.__item_name = item_name
        self.__parent_item = parent_item
        self.__borders = item['geometry']['coordinates']
        self.__border_points = self.__generate_border_points()

        if locations is not None:
            locations[item_name] = self.__border_points

    def __generate_border_points(self):
        if not self.__borders:
            return np.array([])
        return np.array(self.__borders[0])

    @property
    def border_points(self):
        """
        Border points
        """
        return self.__border_points

    @property
    def name(self):
        """
        Item name
        """
        return self.__item_name


class Room(object):

    def __init__(self, room, room_name='', locations=None):
        self._room_name = room_name
        self._borders = room['borders']['geometry']['coordinates']
        self._walls = room['walls']['geometry']['coordinates']
        self._doors = room['doors']['geometry']['coordinates']
        self._items = [Item(item, item_name, locations)
                        for item_name, item in room['items'].items()]
        self._borders_points = self._borders_points()
        self.support_points = []

        if locations is not None:
            locations[room_name] = self._borders_points

    def _borders_points(self):
        """
        Get all border points in matrix form
        """
        points = []
        for border in self._borders:
            points.extend([(b[0], b[1]) for b in border])
        return np.array(points)

    @property
    def borders_points(self):
        return self._borders_points

    @property
    def borders(self):
        return self._borders

    @property
    def walls(self):
        return self._walls

    @property
    def doors(self):
        return self._doors

    @property
    def items(self):
        return self._items

    @property
    def name(self):
        return self._room_name


class Map(object):
    """
    Abstract structure for maps
    """

    def __init__(self, jsonfile):
        with open(jsonfile) as jfile:
            jsonmap = json.load(jfile)
            self.locations = {}
            self.__name = jsonmap['name']
            self.__rooms = [Room(room, room_name, self.locations)
                            for room_name, room in jsonmap['rooms'].items()]
            self.__borders_points = self.__generate_borders_points()
            self.__items_border_points = self.__generate_items_border_points()
            self.__beveled_points = None
            self.__visibility_graph = None
            self.__H = None

    @property
    def name(self):
        """Returns the name of the current graph."""
        return self.__name

    @property
    def visibility_graph(self):
        """
        Get visibility graph
        """
        return self.__visibility_graph

    @property
    def beveled_points(self):
        """
        Get points that are reachable for the robot
        """
        return self.__beveled_points

    @property
    def rooms(self):
        """
        List of all the rooms in the map
        """
        return self.__rooms

    @property
    def borders_points(self):
        """
        Current border points
        """
        return self.__borders_points

    @property
    def items_border_points(self):
        """
        Border points for Items
        """
        return self.__items_border_points

    def __generate_borders_points(self):
        polygon = cascaded_union([Polygon(room.borders_points) for room in self.rooms])
        return np.array(polygon.exterior.coords)[:-1]

    def __generate_items_border_points(self):
        points = []
        for room in self.rooms:
            for item in room.items:
                if item.border_points.shape[0]:
                    points.append(item.border_points)
        return points

    @staticmethod
    def is_valid(line, border, holes):
        """
        Say if the given `line` is valid within `border` and `holes`
        """
        intersects = False
        for hole in holes:
            if hole.touches(line):
                continue
            if hole.intersects(line):
                intersects = True
                break
        return border.contains(line) and not intersects

    def generate_visivility_graph(self, robot):
        width = robot.setting_handler.settings.WIDTH
        large = robot.setting_handler.settings.LARGE
        h = max(width, large)
        h = 0.2 * h

        if not self.__H or self.__H != h:
            self.__H = h
            self.__beveled_points, self.__visibility_graph = self.__generate_visivility_graph()

    def __generate_visivility_graph(self):
        def extend_line(line):
            return np.append(line, [line[0], line[1]], axis=0)

        H = self.__H
        join_style = JOIN_STYLE.mitre

        is_ccw = LinearRing(self.borders_points).is_ccw
        map_po = LineString(extend_line(self.borders_points)).parallel_offset(
            H,
            'left' if is_ccw else 'right',
            join_style=join_style
        )
        if map_po.geom_type == 'MultiLineString':
            geoms = list(map_po.geoms)
            map_po = list(chain(geoms[0].coords, geoms[1].coords))

        self.__support_points = np.array(map_po)
        self.__holes = []

        for item in self.items_border_points:
            if item.size > 0:
                is_ccw = LinearRing(item).is_ccw
                item_po = LineString(extend_line(item)).parallel_offset(
                    H,
                    'right' if is_ccw else 'left',
                    join_style=join_style
                )
                if item_po.geom_type == 'MultiLineString':
                    geoms = list(item_po.geoms)
                    item_po = list(chain(geoms[0].coords, geoms[1].coords))
                support_item_points = np.array(item_po)
                self.__holes.append(support_item_points)

        all_points = self.__support_points

        for hole in self.__holes:
            all_points = np.append(all_points, hole, axis=0)

        holes_p = [Polygon(h) for h in self.__holes]
        border_p = Polygon(self.__support_points)

        points_len = len(all_points)
        visibility_graph = np.zeros(shape=(points_len, points_len))

        for i in range(all_points.shape[0]):
            for j in range(all_points.shape[0]):

                line = np.array((all_points[i], all_points[j]))
                if self.is_valid(LineString(line), border_p, holes_p):
                    visibility_graph[i, j] = True

        return all_points, visibility_graph

    @staticmethod
    def plot_adjacency_graph(all_points, visibility_graph):
        import matplotlib.pyplot as plt
        for i in range(visibility_graph.shape[0]):
            for j in range(visibility_graph.shape[1]):
                if visibility_graph[i, j]:
                    a = all_points[i]
                    b = all_points[j]
                    plt.plot([a[0], b[0]], [a[1], b[1]])
        plt.show()

    def add_points(self, begin, end):
        """
        Add `begin` and `end` points but mantein the structure of
        the graph.
        It returns a copy of `vertices`, `visibility_graph` and `tags` with
        two more values.
        """
        visibility_graph = self.visibility_graph
        all_points = self.beveled_points
        all_points = np.append(all_points, [begin, end], axis=0)

        tags = None

        holes_p = [Polygon(h) for h in self.__holes]
        border_p = Polygon(self.__support_points)

        points_len = len(all_points) - 2
        tvg = np.zeros(shape=(points_len + 2, points_len + 2))
        tvg[:-2, :-2] = visibility_graph
        visibility_graph = tvg

        for i in range(points_len):
            for j in range(points_len, points_len + 2):
                line = np.array((all_points[i], all_points[j]))
                if self.is_valid(LineString(line), border_p, holes_p):
                    visibility_graph[i, j] = visibility_graph[j, i] = True

        # self.plot_adjacency_graph(all_points, visibility_graph)

        return all_points, visibility_graph, tags

def main():
    """
    Main function
    """
    tmap = Map('../maps/map.json')
    print(tmap.visibility_graph)


if __name__ == '__main__':
    main()
