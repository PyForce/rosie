# -*- coding: utf-8 -*-

from heapq import heappush, heappop
from itertools import count
import numpy as np


class AdjacencyMatrixGraph(object):
    """
    Adjacency Matrix Graph
    """
    def __init__(self, vertices, matrix, labels=None):
        self.vertices = vertices
        self.labels = labels
        self.matrix = matrix

    def neighbors(self, u):
        """
        Get all the neighbors of the given vertex index
        """
        return (v for v in range(len(self.vertices)) if self.matrix[u, v])

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

    @staticmethod
    def distance(vertex1, vertex2):
        x, y = vertex1 - vertex2
        return np.hypot(x, y)

    @staticmethod
    def heuristic(vertex1, vertex2):
        return AdjacencyMatrixGraph.distance(vertex1, vertex2)

    # from NetworkX
    def astar_path(self, source, target):
        for i, vertex in enumerate(self.vertices):
            if all(source == vertex):
                s_index = i
                break
        else:
            raise Exception("source vertex '%r' not found" % source)

        c = count()
        queue = [(0, next(c), s_index, 0, None)]

        enqueued = {}
        explored = {}

        while queue:
            _, __, u, path_dist, parent = heappop(queue)
            vertex = self.vertices[u]

            if all(vertex == target):
                path = [self.vertices[u]]
                node = parent
                while node is not None:
                    path.append(self.vertices[node])
                    node = explored[node]
                path.reverse()
                return path

            if u in explored:
                continue

            explored[u] = parent
            for v in self.neighbors(u):
                neighbor = self.vertices[v]

                if v in explored:
                    continue

                ncost = path_dist + self.distance(vertex, neighbor)
                if v in enqueued:
                    qcost, h = enqueued[v]
                    if qcost <= ncost:
                        continue
                else:
                    h = self.heuristic(neighbor, target)
                enqueued[v] = ncost, h
                heappush(queue, (ncost + h, next(c), v, ncost, u))
        raise Exception("target vertex '%r' not found" % target)


if __name__ == '__main__':
    vertices = np.array([
        [0.0, 0.0],
        [1.1, 0.0],
        [2.2, 2.0],
        [2.3, 1.0]
    ])

    matrix = np.array([
        [True, True, False, False],
        [False, True, True, False],
        [True, False, True, True],
        [False, False, True, True]
    ])
    graph = AdjacencyMatrixGraph(vertices, matrix)
    print("from %r to %r" % (vertices[0], vertices[3]))
    print(graph.astar_path(vertices[0], vertices[3]))
