
import json
import numpy as np


Point = lambda x, y: np.array([x, y])
RoomPoint = lambda x, y, room: (np.array([x, y]), room)


class Item(object):

    def __init__(self, item, item_name):
        self._borders = item['geometry']['coordinates']
        self._border_points = self._get_border_points()
        self._item_name = item_name

    def _get_border_points(self):
        points = []
        for border in self.borders:
            points.extend(border)
        return np.matrix(points)

    @property
    def borders(self):
        return self._borders

    @property
    def border_points(self):
        return self._border_points

    @property
    def item_name(self):
        return self._item_name


class Room(object):

    def __init__(self, room, room_name=''):
        self._borders = room['borders']['geometry']['coordinates']
        self._walls = room['walls']['geometry']['coordinates']
        self._doors = room['doors']['geometry']['coordinates']
        self._items = [Item(item) for item in room['items'].values()]
        self._borders_points = self._get_borders_points()
        self._room_name = room_name

    def _get_borders_points(self):
        '''
        Get all border points in matrix form
        :return: m `np.matrix` m[i] = [x_i, y_i]
        '''
        points = []
        for border in self.borders:
            points.extend(border)
        return np.matrix(points)

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
    def room_name(self):
        return self._room_name


class Map(object):

    def __init__(self, jsonfile):
        with open(jsonfile) as f:
            f = json.load(f)
            self._rooms = [Room(room, room_name) for room_name, room in f['rooms'].items()]

    @property
    def rooms(self):
        return self._rooms

    def generate(self):
        pass
