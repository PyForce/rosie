import json
import os

from ..graph_extractor import Map, AdjacencyMatrixGraph as Graph


class Planner(object):

    def __init__(self, mapdir=None):
        self.mapdir = mapdir or os.path.join(os.path.dirname(__file__), '..',
                                             'maps')
        self.__map = None

    def get_points(self, start, end):
        """
        Get points for the trajectory
        """
        return [start, end]

    @property
    def map(self):
        return self.__map

    def use_map(self, map_name):
        self.__map = Map(map_name)
