from ..graph_extractor import Map, AdjacencyMatrixGraph as Graph, list_maps


class Planner(object):

    def __init__(self):
        self.__map = None
        self.__graph = None

        self.__map_mapping = {}
        for map_path, tmap in list_maps():
            self.__map_mapping[tmap['name']] = map_path

    def get_points(self, start, end):
        """
        Get points for the trajectory
        """
        return self.graph.astar_path(start, end)

    def get_points(self, start, end):
        return [start, end]

    @property
    def map(self):
        return self.__map

    @property
    def graph(self):
        return self.__graph

    def use_map(self, map_name):
        """
        Use the located in map_name
        """
        map_path = self.__map_mapping.get(map_name)
        if not map_path:
            raise Warning('Unknown map name %s' % map_name)

        self.__map = Map(map_name)
        vertices = self.map.beveled_points()
        adjacent_matrix = self.map.visibility_graph()
        self.__graph = Graph(vertices, adjacent_matrix)
