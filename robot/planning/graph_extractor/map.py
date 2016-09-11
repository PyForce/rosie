
import json


class Item(object):

    def __init__(self, item):
        self._borders = item['geometry']['coordinates']

    @property
    def borders(self):
        return self._borders


class Room(object):

    def __init__(self, room):
        self._borders = room['borders']['geometry']['coordinates']
        self._walls = room['walls']['geometry']['coordinates']
        self._doors = room['doors']['geometry']['coordinates']
        self._items = [Item(item) for item in room['items'].values()]

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


class Map(object):

    def __init__(self, jsonfile):
        with open(jsonfile) as f:
            f = json.load(f)
            self._rooms = [Room(room) for room in f['rooms'].values()]

    @property
    def rooms(self):
        return self._rooms
