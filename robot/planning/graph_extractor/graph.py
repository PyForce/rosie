# -*- coding: utf-8 -*-


class AdjacencyMatrixGraph(object):
    """
    Adjacency Matrix Graph
    """
    def __init__(self, vertices, matrix, labels=None):
        self.vertices = vertices
        self.labels = labels
        self.matrix = matrix

    def successors(self, point):
        """
        Get all the successors of the given point
        """
        return (v for v in self.vertices if self.matrix[point, v])

    def pos_of(self, tag):
        """
        Get the 'points' for the given tag
        """
        raise NotImplementedError()
        # if type(name) is dict:
        #     try:
        #         n = name['place']
        #         for l in self.L:
        #             if l[0].count(n):
        #                 try:
        #                     return l[1][name['pos']]
        #                 except:
        #                     return l[1][None][0]
        #     except:
        #         pass
        # elif type(name) is str:
        #     for l in self.L:
        #         if l[0].count(name):
        #             return l[1][None][0]
        # elif type(name) is tuple:
        #     for v in self.V:
        #         if v.pos == name:
        #             return v
        # return None
