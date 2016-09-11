# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 21:12:48 2015

@author: Toni
"""
import sys
import time
import datetime
import threading

import robotOLD


__all__ = ['mode', 'sync_exec', 'async_exec', '__version__']

###### INFORMATION ######

__version__ = '1.12'

if sys.version_info.major == 3:
    import queue
else:
    import Queue as queue

#### GLOBAL VARIABLES ####

Q_TEMPORAL = queue.Queue()
Q_NON_TEMPORAL = queue.LifoQueue()

MODE = 'KERNEL'
     # USER
PROCESS = 'SLEEP'
        # EXEC_TEMPORAL
        # EXEC_NON_TEMPORAL

USER_THREAD = False
ROBOT_THREAD = False
CURRENT_COMMAND = None
PREVIOUS_TIMER_NAME = None

ROBOT = robotOLD.Master()

#XXX find another way
KEYS = []

#### PUBLIC FUNCTIONS ####


def mode(mode=None):
    """
    Work mode switcher.

    :param mode: work mode KERNEL/USER
    :type mode: str
    :return: current mode (when ``mode`` isn't set)
    :type: str

    >>> mode('USER')
    >>> mode('KERNEL')
    >>> mode()
    'KERNEL'
    """
    global PROCESS, MODE, USER_THREAD, ROBOT_THREAD
    #---- set USER mode ----
    if mode == 'USER':
        MODE = mode
        PROCESS = 'SLEEP'
        #---- kill kernel thread ----
        if ROBOT_THREAD:
            ROBOT_THREAD = False
            #---- waiting for finishing (robotOLD-thread) ----
            while CURRENT_COMMAND:
                time.sleep(0.1)
        #---- start user thread ----
        if not USER_THREAD:
            _user_thread()
    #---- set KERNEL mode ----
    elif mode == 'KERNEL':
        MODE = mode
        USER_THREAD = False
        PROCESS = 'EXEC_TEMPORAL'
    #---- get mode ----
    else:
        return MODE


def async_exec():
    pass


def sync_exec(command={}):
    """
    Input commands classification.

    :param command: commands
    :type command: dict

    >>> cmd={'start': None, 'end': None,
    ...      'place': 'table', 'pos': 'in',
    ...      'command':'stop'}
    >>> sync_exec(cmd)
    >>> cmd={'path': [(0,0),(1,1)]}
    >>> sync_exec(cmd)
    """
    global PROCESS
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
    #---- mode ----
    if MODE == 'KERNEL':
        PROCESS = 'EXEC_TEMPORAL'

#### PRIVATE FUNCTIONS ####


def _run(event):
    """
    Kernel main thread.
    """
    global PROCESS
    while event.is_set():
        #---- sleep ----
        if PROCESS == 'SLEEP':
            time.sleep(0.5)
        #---- non-temporal command ----
        if PROCESS == 'EXEC_NON_TEMPORAL':
            try:
                _exec_non_temporal_command(Q_NON_TEMPORAL.get_nowait())
            except queue.Empty:
                PROCESS = 'SLEEP'
        #---- temporal command ----
        if PROCESS == 'EXEC_TEMPORAL':
            try:
                _exec_temporal_command(Q_TEMPORAL.get_nowait())
            except queue.Empty:
                PROCESS = 'EXEC_NON_TEMPORAL'
        time.sleep(0.5)


def _exec_non_temporal_command(cmd):
    """
    Execution of a non-temporal command.

    :param cmd: non-temporal command
    :type cmd: dict
    """
    global PROCESS
    Q_NON_TEMPORAL.task_done()
    PROCESS = 'SLEEP'
    _robot_thread(cmd, 'NON_TEMPORAL')


def _exec_temporal_command(cmd):
    """
    Execution of a temporal command.

    Launch a pair of thread (start and end) in new timers.

    :param cmd: temporal command
    :type cmd: dict
    """
    Q_TEMPORAL.task_done()
    today = datetime.datetime.today()
    #---- start time ----
    try:
        ts = (cmd['start']-today).total_seconds()
        if ts < 0:
            return
    except:
        ts = 0
    #---- end time ----
    try:
        te = (cmd['end'] - today).total_seconds()
        if te < 0:
            return
        elif ts and te < ts:
            return
    except:
        te = None
    #---- execute in a new thread ----
    if ts or te:
        t_ident = str(today.microsecond)
        #---- start thread ----
        t_start = threading.Timer(ts, _start_temporal_cmd, [cmd])
        t_start.setName(t_ident)
        t_start.start()
        if te:
            t_end = threading.Timer(te, _end_temporal_cmd, [t_start])
            t_end.setName(t_ident)
            t_end.start()


def _start_temporal_cmd(cmd):
    """
    Start the task of the corresponding pair.

    :param cmd: temporal command
    :type cmd: dict
    """
    global PREVIOUS_TIMER_NAME
    #---- kill previous thread ----
    if PREVIOUS_TIMER_NAME:
        for item in threading.enumerate():
            if item.name == PREVIOUS_TIMER_NAME:
                item.cancel()
    PREVIOUS_TIMER_NAME = threading.current_thread().name
    #---- call robot_thread ----
    _robot_thread(cmd, 'TEMPORAL')


def _end_temporal_cmd(timer):
    """
    Kill the task of the corresponding pair.

    :param timer: timer of start of the corresponding pair
    :type timer: threading.Timer
    """
    global ROBOT_THREAD, PREVIOUS_TIMER_NAME
    timer.cancel()
    if CURRENT_COMMAND[0] == 'TEMPORAL' and \
            PREVIOUS_TIMER_NAME == timer.name:
        ROBOT_THREAD = False
        PREVIOUS_TIMER_NAME = None


def _user_thread():
    """
    Start the thread of the user direct control (asynchronous).
    """
    global USER_THREAD
    USER_THREAD = True
    user_t = threading.Thread(target=_user, name='USER')
    user_t.start()


def _user():
    """
    Thread of the USER mode.
    """
    #XXX find another way
    global KEYS
    x, y, z = 0, 0, 0
    print('USER MODE: STARTED')
    while USER_THREAD:
        dx, dy, dz = 0, 0, 0
        if 87 in KEYS:  # W
            dy += 8
        if 65 in KEYS:  # A
            dx -= 8
        if 83 in KEYS:  # S
            dy -= 8
        if 68 in KEYS:  # D
            dx += 8
        if 81 in KEYS:  # Q
            dz -= 8
        if 69 in KEYS:  # E
            dz += 8

        x = (x+dx)/2.0
        y = (y+dy)/2.0
        z = (z+dz)/2.0

        if dx or dy or round(x, 2) or round(y, 2):
            ROBOT.async_request((x, y))
        elif round(z, 2):
            ROBOT.async_request((0, 0), z)

        time.sleep(0.1)
    ROBOT.end_current_task()
    KEYS = []
    print('USER MODE: ENDED')


def _robot_thread(cmd, cmd_type):
    """
    Start the thread of the robotOLD (synchronous).

    This function controls the access to the only thread of the robotOLD.

    :param cmd: temporal or non-temporal command
    :type cmd: dict
    :param cmd_type: TEMPORAL/NON_TEMPORAL
    :type cmd_type: str
    """
    global CURRENT_COMMAND, ROBOT_THREAD
    #---- kill previous thread ----
    if ROBOT_THREAD:
        ROBOT_THREAD = False
        #---- save or delete the current thread ----
        if CURRENT_COMMAND[0] == 'NON_TEMPORAL':
            Q_NON_TEMPORAL.put_nowait(CURRENT_COMMAND[1])
        elif CURRENT_COMMAND[0] == 'TEMPORAL':
            pass
        #---- waiting for finishing (robotOLD-thread) ----
        while CURRENT_COMMAND:
            time.sleep(0.1)
    #---- kill all thread (when USER mode is set) ----
    if MODE == 'USER':
        return
    #---- start robotOLD thread ----
    ROBOT_THREAD = True
    CURRENT_COMMAND = (cmd_type, cmd)
    robot_t = threading.Thread(target=_robot, name='KERNEL', args=([cmd]))
    robot_t.start()


def _robot(cmd):
    """
    Thread of the KERNEL mode.

    :param cmd: command
    :type cmd: dict
    """
    global PROCESS, ROBOT_THREAD, CURRENT_COMMAND
    print("\n   THREAD: " + str(cmd))
    #---- master request process ----
    ROBOT.sync_request(cmd)
    #---- waiting for finishing (robotOLD-process) ----
    while not ROBOT.is_ended():
        time.sleep(0.5)
        #==== BREAK CODE ====
        if not ROBOT_THREAD:
            ROBOT.end_current_task()
            while not ROBOT.is_ended():
                time.sleep(0.1)
            ROBOT_THREAD = False
            CURRENT_COMMAND = None
            print('   THREAD STATUS: BREAK')
            return
    ROBOT_THREAD = False
    CURRENT_COMMAND = None
    PROCESS = 'EXEC_TEMPORAL'
    print('   THREAD STATUS: END')
