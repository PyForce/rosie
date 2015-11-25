# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 11:02:54 2015

@author: Toni
"""

__all__=[]

###### IMPORT ######

import os
import logging

###### GLOBAL VARIABLES ######
#---- __init__ ----
LANGUAGE='EN'
#---- languages ----
DRAW=False
USER='User'
#---- log ----
LOG_ENABLE=False
LOG_PATH=''
_IS_LOG_CONFIG=False

#### COMMANDS ####
class Common_Commands():
    """
    Event for process of common commands: go, move, speed, turn.
    """
    def __init__(self,cmd=[]):
        self.CMD=[]
        for item in cmd:
            d={}
            for key in item[0].keys():
                d[key]=item[0][key]
            for key in item[1].keys():
                d[key]=item[1][key]
            for key in item[2].keys():
                d[key]=item[2][key]
            self.CMD.append(d)
    
    def __str__(self):
        return str(self.CMD)
        
class Urgent_Commands():
    def __init__(self,cmd=[]):
        self.CMD=cmd
        
    def __str__(self):
        return str(self.CMD)
        
class None_Commands():
    def __init__(self,cmd=[]):
        self.CMD=cmd
        
    def __str__(self):
        return str(self.CMD)
    
#### FUNCTIONS ####
def log(info='',user=''):
    if LOG_ENABLE and info:
        logging.debug(user+': '+str(info))

def log_enable(enable):
    global LOG_ENABLE, _IS_LOG_CONFIG
    LOG_ENABLE=enable
    if LOG_ENABLE:
        if not _IS_LOG_CONFIG:
            log_config()

def log_config(log_name='NLP',log_path=''):
    global _IS_LOG_CONFIG, LOG_PATH
    if _IS_LOG_CONFIG:
        return
    #---- filename ----
    if log_name:
        if not log_name.endswith('.log'):
            log_name=log_name+'.log'
    else:
        log_name='NLP.log'
    #---- dir ----
    if os.path.isdir(log_path):
        if not log_name.endswith('/'):
            log_path=log_path+'/'
    else:
        log_path=''
    #---- logging ----
    logging.basicConfig(filename=log_path+log_name,
                        level=logging.DEBUG,
                        format='%(asctime)s %(message)s')
    LOG_PATH=log_path+log_name
    _IS_LOG_CONFIG=True
    
def list_in_list(lin, lout, ptime=False):
    #---- empty list ----
    if lin==[]:
        return False
    #---- move ---
    if ptime:
        pass
    else:
        try:
            if lin[0][0]=='time':
                cmd=lin[1]
            else:
                cmd=lin[0]
            if cmd[0]=='move' and cmd[1]=={}:
                for cout in lout:
                    if cout[0] in ['move','go','turn','speed']:
                        return True
        except: pass
    #---- items ----
    status_cmd=True
    iter_lout=0
    for i in range(len(lin)):
        if status_cmd:
            for j in range(len(lout)):
                #---- check action ----
                if lin[i][0]==lout[j][0]:
                    #---- get parameters ----
                    key=list(lin[i][1].keys())
                    try:
                        key.remove('unit')
                    except: pass
                    #---- check parameters ----
                    status_param=True
                    for k in key:
                        try:
                            if lin[i][1][k]!=lout[j][1][k]:
                                status_param=False
                                break
                        except: return False
                    if status_param:
                        status_cmd=False
                        iter_lout=j
                        break
            if status_cmd:
                return False
        else:
            iter_lout=iter_lout+1
            try:
                #---- check action ----
                if lin[i][0]==lout[iter_lout][0]:
                    #---- get parameters ----
                    key=list(lin[i][1].keys())
                    try:
                        key.remove('unit')
                    except: pass
                    #---- check parameters ----
                    status_param=True
                    for k in key:
                        try:
                            if lin[i][1][k]!=lout[iter_lout][1][k]:
                                return False
                        except: return False
                else:
                    return False
            except: return False
    return True
