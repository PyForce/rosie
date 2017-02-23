"""
Map tools
"""

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
    for tmap in os.listdir(mapdir):
        map_path = os.path.abspath(os.path.join(mapdir, tmap))
        with open(map_path, 'r') as map_file:
            yield map_path, json.load(map_file)


class Item(object):
    """
    Abstraction structure for Items
    """
    def __init__(self, item, item_name='', parent_item=None):
        self.__item_name = item_name
        self.__parent_item = parent_item
        self.__borders = item['geometry']['coordinates']
        self.__border_points = self.__generate_border_points()

    def __generate_border_points(self):
        points = np.array([])
        for border in self.__borders:
            np.append(points, border)
        return np.array(points)

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

    def __init__(self, room, room_name=''):
        self._room_name = room_name
        self._borders = room['borders']['geometry']['coordinates']
        self._walls = room['walls']['geometry']['coordinates']
        self._doors = room['doors']['geometry']['coordinates']
        self._items = [Item(item, item_name) for item_name, item in room['items'].items()]
        self._borders_points = self._borders_points()
        self.support_points = []

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
            self.__rooms = [Room(room, room_name) for room_name, room in jsonmap['rooms'].items()]
            self.__borders_points = self.__generate_borders_points()
            self.__items_border_points = self.__generate_items_border_points()
            self.__beveled_points, self.__visibility_graph = self.__generate_visivility_graph()

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
        points = np.array([])
        for room in self.rooms:
            for item in room.items:
                np.append(points, item.border_points)
        return points

    def __generate_visivility_graph(self):
        def extend_line(line):
            return np.append(line, [line[0], line[1]], axis=0)

        def is_valid(line, border, holes):
            intersects = False
            for hole in holes:
                if hole.touches(line):
                    continue
                if hole.intersects(line):
                    intersects = True
                    break
            return border.contains(line) and not intersects

        # TODO: Move to the constructor
        H = 0.1
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
        support_points = np.array(map_po)

        holes = []

        for item in self.items_border_points:
            if item.size > 0:
                is_ccw = LinearRing(item).is_ccw
                item_po = LineString(extend_line(item)).parallel_offset(
                    H,
                    'right' if is_ccw else 'left',
                    join_style=join_style
                )
                support_item_points = np.array(item_po)
                holes.append(support_item_points)

        all_points = support_points

        for hole in holes:
            all_points = np.append(all_points, hole, axis=0)

        holes_p = [Polygon(h) for h in holes]
        border_p = Polygon(support_points)

        points_len = len(all_points)
        visibility_graph = np.zeros(shape=(points_len, points_len))

        for i in range(all_points.shape[0] - 1):
            for j in range(all_points.shape[0] - 1):

                line = np.array((all_points[i], all_points[j]))
                if is_valid(LineString(line), border_p, holes_p):
                    visibility_graph[i, j] = True

        return all_points, visibility_graph


def main():
    """
    Main function
    """
    tmap = Map('../maps/map.json')
    print tmap.visibility_graph


if __name__ == '__main__':
    main()
