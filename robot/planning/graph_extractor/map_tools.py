
import json
import numpy as np

from shapely.geometry import Polygon, LinearRing, LineString
from shapely.ops import cascaded_union


class Item(object):

    def __init__(self, item, item_name=''):
        self._borders = item['geometry']['coordinates']
        self._item_name = item_name
        self._border_points = self._border_points()

    def _border_points(self):
        points = []
        for border in self._borders:
            points.extend(border)
        return np.array(points)

    @property
    def border_points(self):
        return self._border_points

    @property
    def name(self):
        return self._item_name


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
        '''
        Get all border points in matrix form
        :return: m `np.matrix` m[i] = [x_i, y_i]
        '''
        points = []
        for border in self._borders:
            points.extend([(b[0], b[1]) for b in border])
        return np.array(points)

    @property
    def borders_points(self):
        return self._borders_points

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

    def __init__(self, jsonfile):
        with open(jsonfile) as f:
            jsonmap = json.load(f)
            self._rooms = [Room(room, room_name) for room_name, room in jsonmap['rooms'].items()]
            self._borders_points = self._borders_points()
            self._items_border_points = self._items_border_points()

            self._generate_polygon()

    @property
    def rooms(self):
        return self._rooms

    def _borders_points(self):
        polygon = cascaded_union([Polygon(room.borders_points) for room in self.rooms])
        return np.array(polygon.exterior.coords)[:-1]

    def _items_border_points(self):
        points = []
        for room in self.rooms:
            for item in room.items:
                points.append(item.border_points)
        return points

    def _generate_polygon(self):
        def extend_line(line):
            return np.append(line, [line[0], line[1]], axis=0)

        def plot_line(line, support_line):
            line = np.array(line)
            support_line = np.array(support_line)

            plt.plot(line[:,0], line[:,1], 'r')
            plt.plot(support_line[:,0], support_line[:,1], 'y')

        def is_valid(line, border, holes):
            intersects = False
            for hole in holes:
                if hole.touches(line):
                    continue
                if hole.intersects(line):
                    intersects = True
                    break
            return border.contains(line) and not intersects

        import matplotlib.pyplot as plt

        # TODO: Move to the constructor
        H = 0.1
        JOIN_STYLE = 1

        items_border_points = self.items_border_points

        is_ccw = LinearRing(self.borders_points).is_ccw
        map_po = LineString(extend_line(self.borders_points)).parallel_offset(
            H,
            'left' if is_ccw else 'right',
            join_style=JOIN_STYLE
        )
        support_points = np.array(map_po)

        holes = []

        for item in self.items_border_points:
            if item.size > 0:
                is_ccw = LinearRing(item).is_ccw
                item_po = LineString(extend_line(item)).parallel_offset(
                    H,
                    'right' if is_ccw else 'left',
                    join_style=JOIN_STYLE
                )
                support_item_points = np.array(item_po)
                holes.append(support_item_points)

                plot_line(item, support_item_points)

        all_points = support_points

        for hole in holes:
            all_points = np.append(all_points, hole, axis=0)

        holes_p = [Polygon(h) for h in holes]
        border_p = Polygon(support_points)

        c = 1000

        for i in range(all_points.shape[0] - 1):
            for j in range(all_points.shape[0] - 1):
                if not c:
                    break
                c -= 1

                line = np.array((all_points[i], all_points[j]))
                if is_valid(LineString(line), border_p, holes_p):
                    plt.plot(line[:,0], line[:,1], 'b')

        plot_line(self.borders_points, support_points)

        plt.gca().axis('off')
        plt.gca().set_aspect(1)
        plt.show()

    @property
    def borders_points(self):
        return self._borders_points

    @property
    def items_border_points(self):
        return self._items_border_points


m = Map('../maps/map.json')
