# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 21:12:48 2015

@author: Toni
"""

__all__=['execute']

#### import ####
try:
    import queue
except:
    import Queue as queue
try:
    import _thread
except:
    import thread as _thread

import time, datetime, threading
from threading import Timer, Thread

#XXX editar
import robot

#### global variables ####
Q_TEMPORAL=queue.Queue()
Q_NON_TEMPORAL=queue.LifoQueue()

MODE='USER'
     # KERNEL
PROCESS='SLEEP'    
        # EXEC_TEMPORAL
        # EXEC_NON_TEMPORAL

KEYS=[]
MASTER=robot.Master()

USER_THREAD=False
ROBOT_THREAD=False
CURRENT_COMMAND=None
PREVIOUS_TIMER_NAME=None

#### functions ####
def link_robot(function):
    MASTER.motion.SEND_POSITION=function

def execute(command,mode=None):
    """       
    Classification of the input commands.
    
    :param command: commands
    :type command: list(str,dict))
    :param mode: work mode USER/KERNEL
    :type mode: str
    
    >>> cmd={'start': None, 'end': None,
    ...      'place': 'table', 'pos': 'in',
    ...      'action':'stop'}
    >>> execute(cmd)
    """
    global PROCESS, MODE, USER_THREAD
    #---- commands classification ----
    if command:
        try:
            #---- temporal command ----
            if command['start'] or command['end']:
                Q_TEMPORAL.put_nowait(command)
            #---- non-temporal command ----
            else:
                Q_NON_TEMPORAL.put_nowait(command)
        except KeyError:
            Q_NON_TEMPORAL.put_nowait(command)
    #---- switch: mode ----    
    MODE=mode
    if MODE=='USER':
        PROCESS='SLEEP'
        if not USER_THREAD:
            _user_thread()
    else:
        USER_THREAD=False
        PROCESS='EXEC_TEMPORAL'

def _run():
    """
    Main thread of the planner of execution.
    """
    global PROCESS
    while True:
        #---- sleep ----
        if PROCESS=='SLEEP':
            time.sleep(0.5)
        #---- non-temporal command ----
        if PROCESS=='EXEC_NON_TEMPORAL':
            try:
                _exec_non_temporal_command(Q_NON_TEMPORAL.get_nowait())
            except queue.Empty:
                PROCESS='SLEEP'
        #---- temporal command ----
        if PROCESS=='EXEC_TEMPORAL':
            try:
                _exec_temporal_command(Q_TEMPORAL.get_nowait())
            except queue.Empty:
                PROCESS='EXEC_NON_TEMPORAL'
        time.sleep(0.5)

def _exec_non_temporal_command(cmd):
    """
    Execution of a non-temporal command.
    
    :param cmd: non-temporal command
    :type commands: list(str,dict))
    """
    Q_NON_TEMPORAL.task_done()
    global PROCESS
    PROCESS='SLEEP'
    _robot_thread(cmd,'NON_TEMPORAL')

def _exec_temporal_command(cmd):
    """
    Execution of a temporal command.
    
    Launch a pair of thread (start and end) in new timers.
    
    :param cmd: temporal command
    :type cmd: list(str,dict))
    """
    Q_TEMPORAL.task_done()
    today=datetime.datetime.today()
    #---- start time ----
    try:
        ts=(cmd[0]['start']-today).total_seconds()
        if ts<0:
            return
    except:
        ts=0
    #---- end time ----
    try:
        te=(cmd[0]['end'] - today).total_seconds()
        if te<0:
            return
        elif ts and te<ts:
            return
    except:
        te=None
    #---- execute in a new thread ----
    if ts or te:
        t_ident=str(today.microsecond)
        #---- start thread ----
        t_start=Timer(ts, _start_temporal_cmd, [cmd])
        t_start.setName(t_ident)
        t_start.start()
        if te:
            t_end=Timer(te, _end_temporal_cmd, [t_start])
            t_end.setName(t_ident)
            t_end.start()

def _end_temporal_cmd(timer):
    """
    Kill the task of the corresponding pair.
    
    :param timer: timer of start of the corresponding pair  
    :type timer: Timer
    """
    global ROBOT_THREAD, PREVIOUS_TIMER_NAME
    timer.cancel()
    if CURRENT_COMMAND[0]=='TEMPORAL' and \
            PREVIOUS_TIMER_NAME==timer.name:
        ROBOT_THREAD=False
        PREVIOUS_TIMER_NAME=None

def _start_temporal_cmd(cmd):
    """
    Start the task of the corresponding pair.
    
    :param cmd: temporal command
    :type cmd: list(str,dict)) 
    """
    global PREVIOUS_TIMER_NAME
    #---- kill previous thread ----
    if PREVIOUS_TIMER_NAME:
        for item in threading.enumerate():
            if item.name==PREVIOUS_TIMER_NAME:
                item.cancel()
    PREVIOUS_TIMER_NAME=threading.current_thread().name
    #==== ROBOT USER-CODE ====
    _robot_thread(cmd, 'TEMPORAL')

def _user_thread():
    """
    Start the thread of the user direct control.
    """
    global USER_THREAD
    USER_THREAD=True
    robot=Thread(target=_user, name='USER')
    robot.start()

def _user():
    """
    Thread of the USER mode.
    """
    global KEYS
    x, y = 0, 0
    print('USER MODE: STARTED')
    while USER_THREAD:
        dx, dy = 0, 0
        if 87 in KEYS:  # W
            dy+=8
        if 65 in KEYS:  # A
            dx-=8
        if 83 in KEYS:  # S
            dy-=8
        if 68 in KEYS:  # D
            dx+=8
        x=(x+dx)/2.0
        y=(y+dy)/2.0
        MASTER.process_user_request((x,y))
        time.sleep(0.1)
    MASTER.end_current_task()
    KEYS=[]
    print('USER MODE: ENDED')

def _robot_thread(cmd, cmd_type):
    """
    Start the thread of the robot.
    
    This function controls the access to the only thread of the robot.
    
    :param cmd: temporal or non-temporal command
    :type cmd: list(str,dict))
    :param cmd_type: type of command
    :type cmd_type: str 
    """
    global CURRENT_COMMAND, ROBOT_THREAD
    #---- kill previous thread ----
    if ROBOT_THREAD:
        ROBOT_THREAD=False
        #---- save or delete the current thread ----
        if CURRENT_COMMAND[0]=='NON_TEMPORAL':
            Q_NON_TEMPORAL.put_nowait(CURRENT_COMMAND[1])
        elif CURRENT_COMMAND[0]=='TEMPORAL':
            pass
        #---- waiting for finishing (robot-thread) ----
        while CURRENT_COMMAND:
            pass
    #---- kill all thread in USER mode ----
    if MODE=='USER':
        return
    #---- start robot thread ----
    ROBOT_THREAD=True
    CURRENT_COMMAND=(cmd_type,cmd)
    robot=Thread(target=_robot, name='ROBOT', args=([cmd]))
    robot.start()

def _robot(cmd):
    """
    Thread of the robot.
    
    :param cmd: command
    :type cmd: list(str,dict))
    """
    global PROCESS, ROBOT_THREAD, CURRENT_COMMAND
    print("\n   THREAD: " + str(cmd))
    #---- start master process ----
    #XXX add the master processing of the command 
    MASTER.process_request(cmd)
    #---- waiting for finishing (robot-process) ----
    #XXX cambiar la condicion de parada del master
    while not MASTER.is_ended():
        time.sleep(0.5)
        ################################################
        if not ROBOT_THREAD:                         ###
            MASTER.end_current_task()                        ###
            while not MASTER.is_ended():          ###
                time.sleep(0.5)                      ###
            ROBOT_THREAD=False                       ### BREAK
            CURRENT_COMMAND=None                     ### CODE
            print('   THREAD STATUS: BREAK')           #
            # experiment.add_time('break robot thread')#
            return                                   ###
        ################################################
    ROBOT_THREAD=False
    CURRENT_COMMAND=None
    PROCESS='EXEC_TEMPORAL'
    print('   THREAD STATUS: END')
    # experiment.add_time('end robot thread')
    # experiment.print_time()

#==== RUN PROCESS ====
_thread.start_new_thread(_run,())
