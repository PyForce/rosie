# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 0:30:00 2015

@author: Sisi
"""

import heapq
from math import sqrt


class HeapState:

    def __init__(self, item, priority):
        self.item = item
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority


def distance(u, v):
    if type(u) is tuple:
        X = v[0] - u[0]
        Y = v[1] - u[1]
    else:
        X = v.pos[0] - u.pos[0]
        Y = v.pos[1] - u.pos[1]
    return sqrt(X * X + Y * Y)


def _construct_path(path, start, node):
    final_path = [node]
    while path[node] != start:
        node = path[node]
        final_path.append(node)
    final_path.append(start)
    return reversed(final_path)


def search(G, s, t):
    if s == t:
        return [s]
    path = {s: None}
    visit = {s: 1}
    heap = []
    heapq.heappush(heap, HeapState(s, 0))
    count = 1
    while count:
        pq = heapq.heappop(heap)
        node = pq.item
        count -= 1
        for suc in G.succs(node):
            try:
                visit[suc]
                continue
            except:
                if t == suc:
                    path[suc] = node
                    path = list(_construct_path(path, s, t))
                    mindist = 0
                    try:
                        point = path[0]
                        for item in path[1:]:
                            mindist += distance(point, item)
                            point = item
                    except:
                        return []
                    return path
                path[suc] = node
                visit[suc] = 1
                heapq.heappush(
                    heap, HeapState(suc, pq.priority + distance(node, suc)))
                count += 1
    return list(node)


def search_with_distance(G, s, t):
    if s == t:
        return (0, [s])
    path = {s: None}
    visit = {s: 1}
    heap = []
    heapq.heappush(heap, HeapState(s, 0))
    count = 1
    while count:
        pq = heapq.heappop(heap)
        node = pq.item
        count -= 1
        for suc in G.succs(node):
            try:
                visit[suc]
                continue
            except:
                if t == suc:
                    path[suc] = node
                    path = list(_construct_path(path, s, t))
                    mindist = 0
                    try:
                        point = path[0]
                        for item in path[1:]:
                            mindist += distance(point, item)
                            point = item
                    except:
                        return (0, [])
                    return (mindist, path)
                path[suc] = node
                visit[suc] = 1
                heapq.heappush(
                    heap, HeapState(suc, pq.priority + distance(node, suc)))
                count += 1
    path = list(node)
    mindist = 0
    try:
        point = path[0]
        for item in path[1:]:
            mindist += distance(point, item)
            point = item
    except:
        return (0, [])
    return (mindist, path)
