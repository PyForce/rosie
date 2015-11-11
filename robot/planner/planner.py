# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 17:07:02 2015

@author: Toni
"""

__all__=['set_map', 'path_xyt']

#### import ####
import os
from robot.planner.searcher import astar
from robot.planner.maps import graph

#### global variables ####
METRIC_TIME=5 #seconds
MAP=None

PATH_MAP= os.path.join(os.getcwd(), "robot", "planner", "maps")

def set_map(file_name=''):
    """
    Set map.
    
    :param file_name: name of the map 
    :type file_name: str
    """
    global MAP
    #---- fix the name ----
    if not file_name.endswith('.py'):
        file_name=file_name+'.py'
    #---- check and load the map ----
    map_file=os.path.join(PATH_MAP,file_name)
    if os.path.exists(map_file):
        try:
            raw=open(map_file,'rU').read()
            exec(raw)
            MAP=locals()['CURRENT_MAP']
        except:
            MAP=None
    else:
        MAP=None

def path_xyt(start,target,show=False):
    """
    Generation of path.
    
    :param start: current position of the robot 
    :type start: tuple(float,float), str, list(tuple(float,float))
    :param target: destination place
    :type target: tuple(float,float), str, list(tuple(float,float))
    :return: x, y and t values
    :type: dict(str:list(float))
    
    >>> path_xyt((0,0),'hall')
    {'x_planning': [0, 0.9],
     'y_planning': [0, -0.9],
     't_planning': [0, 6.4]}
    """
    x,y,t=[],[],[]
    path_list=_get_path(start,target,show)
    #---- generate the vector of time ----
    if len(path_list)>1:
        prev_point=path_list[0]
        x.append(prev_point[0])
        y.append(prev_point[1])
        t.append(0)
        for item in path_list[1:]:
            x.append(-item[0])
            y.append(item[1])
            metric=astar.distance(prev_point,item)*METRIC_TIME
            t.append(round(metric,1))
            prev_point=item      
        path_dict={'x_planning':y, 'y_planning':x, 't_planning':t}
        return path_dict
    return {}

def _get_path(start,target,show=False):
    path_list=[]
    #---- with map ----
    if MAP:
        #---- start ----
        if type(start) is dict:
            START_POINT=MAP.pos_of(start)
        elif type(start) is str:
            START_POINT=MAP.pos_of(start)
        elif type(start) is tuple:
            start=start[:2]
            START_POINT=MAP.pos_of(_pos_approach(start))
        elif type(start) is graph.Node:
            START_POINT=start
        else:
            START_POINT=None
        #---- target ----    
        if type(target) is dict:
            try:
                TARGET_POINT=target['path']
            except:
                TARGET_POINT=MAP.pos_of(target)
        elif type(target) is str:
            TARGET_POINT=MAP.pos_of(target)
        elif type(target) is tuple:
            TARGET_POINT=MAP.pos_of(_pos_approach(target))
        elif type(target) is graph.Node:
            TARGET_POINT=target
        else:
            TARGET_POINT=None
        #---- path ----
        try:
            if type(TARGET_POINT) is list:
                path=astar.search(MAP, START_POINT, TARGET_POINT[0])
            else:
                path=astar.search(MAP, START_POINT, TARGET_POINT)
            path_list=[item.pos for item in path]
        except: return []
        if path_list:
            if type(start) is tuple:
                if path_list[0]!=start:
                    path_list.insert(0,start)
            if type(target) is tuple:
                if path_list[-1]!=target:
                    path_list.append(target)
            try:
                if type(TARGET_POINT) is list:
                    for item in TARGET_POINT[1:]:
                        path_list.append(item.pos) 
            except: pass
        else:
            try:
                if type(TARGET_POINT) is list and TARGET_POINT:
                    for item in TARGET_POINT:
                        path_list.append(item.pos) 
            except: pass
    #---- without map ----
    else:
        pass
    if show:
        for item in path_list:
            print(str(item))
    return path_list
    
def _pos_approach(p):
    global MAP
    if len(MAP.V)>1:
        point=(0,0)
        mindist_point=2**32
        for v in MAP.V:
            mindist=astar.distance(p,v.pos)
            if mindist<mindist_point:
                mindist_point=mindist
                point=v.pos
        return point
    return (0,0)
    
set_map("Gustavo's house")