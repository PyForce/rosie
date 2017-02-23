import json
import os

from ..graph_extractor import Map


class Planner(object):

    def __init__(self, mapdir=None):
        self.mapdir = mapdir or os.path.join(os.path.dirname(__file__), '..',
                                             'maps')
        self.__map = {}

    def get_points(self, start, end):
        """
        Get points for the trajectory
        """
        return [start, end]

    @property
    def map(self):
        return self.__map

    @map.setter
    def map(self, value):
        # interpret string as map name
        if isinstance(value, str):
            self.__map = self.get_map(value)
        # receive dict for new map
        elif isinstance(value, dict):
            self.__map = value.copy()
        # transform self._map in the corresponding graph
        self.graph = None

    def use_map(self, map_name):
        self.__map = self.get_map(map_name)

    def get_map(self, map_name, mapdir=None):
        for map in self.list_maps(mapdir):
            if map['name'] == map_name:
                return map
