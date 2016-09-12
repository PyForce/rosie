import os
import json


class Planner(object):
    def __init__(self, mapdir=None):
        self.mapdir = mapdir or os.path.join(os.path.dirname(__file__), '..',
                                             'maps')

    @property
    def map(self):
        return self._map

    @map.setter
    def map(self, value):
        # interpret string as map name
        if isinstance(value, str):
            self._map = self.get_map(value)
        # receive dict for new map
        elif isinstance(value, dict):
            self._map = value.copy()
        # transform self._map in the corresponding graph
        self.graph = None

    def maps(self, dir=None):
        """
            Iterator that yields map objects content
        """
        folder = dir or self.mapdir
        for map in os.listdir(folder):
            with open(os.path.join(folder, map), 'r') as map_file:
                yield json.load(map_file)

    def get_map(self, map_name, dir=None):
        for map in self.maps(dir):
            if map['name'] == map_name:
                return map
