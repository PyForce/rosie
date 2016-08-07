# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 17:07:02 2015

@author: Toni
"""
import importlib

from robot.planner.maps import graph
from robot.planner.searcher import astar


__all__ = ['set_map', 'path_xyt']

###### INFORMATION ######

__version__ = '1.12'

#### IMPORT ####

#---- Python import ----

#---- rOSi import ----

#### GLOBAL VARIABLES ####

MAP = None
METRIC_TIME = 5  # in seconds
PATH_MAP = 'robot.planner.maps'

#### PUBLIC FUNCTIONS ####


def set_map(file_name=''):
    """
    Set map.

    The map should be defined in the folder robot.planner.maps

    :param file_name: name of the map
    :type file_name: str

    >>> set_map("Gustavo's house")
    """
    global MAP
    #---- fix the name ----
    file_name.rstrip('.py')
    #---- check and load the map ----
    try:
        raw = importlib.import_module('%s.%s' % (PATH_MAP, file_name))
        MAP = raw.CURRENT_MAP
    except:
        MAP = None
        print("    WARNING: Map information wasn't loaded")


def path_xyt(start, target, show=True):
    """
    Generation of path.

    :param start: current position of the robot
    :type start: tuple, str, list
    :param target: destination place
    :type target: tuple, str, list, dict
    :param show: show the found place
    :type show: bool
    :return: x, y and t values
    :type: dict

    >>> path_xyt((0,0,0),'hall')
    {'x_planning': [0, 0.9],
     'y_planning': [0, -0.9],
     't_planning': [0, 6.4]}
    """
    x, y, t = [], [], []
    path_list = []
    #---- path based in list of points ----
    try:
        path_list = target['path']
        if type(start) is tuple:
            path_list.insert(0, start[:2])
        if len(path_list) > 1:
            new_list = []
            for i in range(len(path_list)-1):
                new_list.extend(_get_path(path_list[i], path_list[i+1]))
            path_list = new_list
    #---- path based in tuple or text ----
    except KeyError:
        path_list = _get_path(start, target)
    #---- show the generated path ----
    if show:
        for item in path_list:
            print(str(item))
    #---- generate the vector of time ----
    if len(path_list) > 1:
        prev_point = path_list[0]
        x.append(prev_point[0])
        y.append(prev_point[1])
        t.append(0)
        for item in path_list[1:]:
            x.append(-item[0])
            y.append(item[1])
            metric = astar.distance(prev_point, item)*METRIC_TIME
            t.append(round(metric, 1))
            prev_point = item
        path_dict = {'x_planning': y, 'y_planning': x, 't_planning': t}
        return path_dict
    return {}

#### PRIVATE FUNCTIONS ####


def _get_path(start, target):
    path_list = []
    #---- with map ----
    if MAP:
        #---- start ----
        if type(start) is tuple:
            START_POINT = MAP.pos_of(_pos_approach(start[:2]))
        #---- target ----
        if type(target) is dict:
            TARGET_POINT = MAP.pos_of(target)
        elif type(target) is str:
            TARGET_POINT = MAP.pos_of(target)
        elif type(target) is tuple:
            TARGET_POINT = MAP.pos_of(_pos_approach(target[:2]))
        elif type(target) is graph.Node:
            TARGET_POINT = target
        else:
            TARGET_POINT = None
        #---- generate path with any search algoritm ----
        try:
            if type(TARGET_POINT) is list:
                path = astar.search(MAP, START_POINT, TARGET_POINT[0])
            else:
                path = astar.search(MAP, START_POINT, TARGET_POINT)
            path_list = [item.pos for item in path]
        except:
            return []
        #---- try to complete the path ----
        if path_list:
            if type(start) is tuple:
                if path_list[0] != start[:2]:
                    path_list.insert(0, start[:2])
            if type(target) is tuple:
                if path_list[-1] != target[:2]:
                    path_list.append(target[:2])
            try:
                if type(TARGET_POINT) is list:
                    for item in TARGET_POINT[1:]:
                        path_list.append(item.pos)
            except:
                pass
    #---- without map ----
    else:
        pass
    return path_list


def _pos_approach(p):
    global MAP
    if len(MAP.V) > 1:
        point = (0, 0)
        mindist_point = 2**32
        for v in MAP.V:
            mindist = astar.distance(p, v.pos)
            if mindist < mindist_point:
                mindist_point = mindist
                point = v.pos
        return point
    return (0, 0)

set_map("Gustavo's house")
