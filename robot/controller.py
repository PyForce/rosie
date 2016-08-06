# -*- coding: utf-8 -*-
import math
import os
import sys
import time
from datetime import datetime
import importlib

import settings.config as global_settings
from robot.control import pid, track
from robot.load import SETTINGS as settings


__all__=['Controller', '__version__']

###### INFORMATION ######

__version__ = '1.12'

#### IMPORT ####

#---- Python import ----
# On Windows
if sys.platform.startswith('win'):
    print('    PLATFORM: Windows')
    import threading
# On UNIX & OS X
else:
    print('    PLATFORM: UNIX or OS X')
    import signal

#---- rOSi import ----

#==== import and load the robot control board ====
board = None
if os.path.exists(os.path.join(os.getcwd(), 'robot', 'boards',
                  settings.FILENAME)):
    # TODO: Change this crab to something less painfull for debugging
    try:
        board = importlib.import_module('robot.boards.%s' %
                                        settings.FILENAME[:-3])
        print('    NAME: '+settings.MOBILE_ROBOT)
    except:
        board=None

#### CLASS ####

class Controller:
    def __init__(self):
        try:
            self.robot=board.Board()
            try:
                self.robot.set_constants(settings.CONST_KC,
                                         settings.CONST_KI,
                                         settings.CONST_KD)
            except: pass
        except:
            print("    ERROR: The control board wasn't loaded")
            self.robot=None
            
        #---- position ----
        self.x_position = 0
        self.y_position = 0
        self.z_position = 0
        #---- encoders ----
        self.encoder1 = 0
        self.encoder2 = 0
        self.prev_encoder1 = 0
        self.prev_encoder2 = 0
        self.prev_delta_encoder_1 = 0
        self.prev_delta_encoder_2 = 0
        #---- others ----
        self.smooth = True
        self.finished = True 
        self.count = 0        
        self.sample_time = 0.05
        self.action = 'stop'
        self.SEND_POSITION = lambda x, y, theta: None
        self.COUNTER_POS = 0
        self.reference = track.Track()
        self._start_move=None   
        self.motion=None
        self.angle=0
        self.difference=2*math.pi
        self.request=None
        
        self.log_file=None
        if global_settings.LOG:
            self.log_file=open(os.path.join(os.getcwd(),'logs',"pos.log"),'w')      
        
        # On Windows
        if sys.platform.startswith('win'):
            self.next_call=0
            self._start_move=self._win_timer_start
        # On UNIX & OS X
        else:
            try:
                signal.signal(signal.SIGALRM, self._unix_handler)
                signal.setitimer(signal.ITIMER_REAL, 0, 0)
            except:
                print("    ERROR: Signal initializing")
            self._start_move=self._unix_timer_start

    def set_speed(self,set1=0, set2=0):
        """
        Set speed of the wheels.
        
        :param set1: set point of the right wheel  
        :type set1: float
        :param set2: set point of the left wheel  
        :type set2: float

        >>> controller=Controller()        
        >>> controller.set_speed(2.0,1.5)
        """
        if self.robot:
            self.robot.set_speeds(set1, set2)
    
    def get_state(self):
        """
        Return the state of the encoders and the battery level.
        
        :return: encoders an battery state  
        :type: tuple

        >>> controller=Controller()        
        >>> controller.get_state()
        (0.0, 0.0, 0.9)        
        """
        if self.robot:
            return self.robot.read_state()

    def move(self, trace, smooth=True):
        """
        Start the movement of the robot.
        
        :param trace: track parameters
        :type trace: dict
        :param smooth: flag for smooth movement  
        :type smooth: bool

        >>> track={'x_planning': [0, 0.9],
        ...        'y_planning': [0, -0.9],
        ...        't_planning': [0, 6.4]}
        >>> controller=Controller()
        >>> controller.move(track)
        """
        self.motion="move"
        self.smooth = smooth
        #---- reset counter and PID (software) ----
        self.count = 0      
        if not settings.PID:
            pid.reset()
        #---- start the movement ----
        trace['sample_time']= self.sample_time    
        self.reference.generate(**trace)
        self.finished = False
        self._start_move()

    def rotate(self, angle):
        self.motion="rotate"
        self.angle=angle
        self.difference=2**32
        #---- reset counter and PID (software) ----
        self.count = 0      
        if not settings.PID:
            pid.reset()
        #---- start the rotation ----
        self.finished = False
        self._start_move()

    def end_move(self):
        """
        Finishes the movement unavoidably.
        
        >>> controller=Controller()        
        >>> controller.end_move()
        """
        # On UNIX or OS X
        if not sys.platform.startswith('win'):
            try:
                signal.setitimer(signal.ITIMER_REAL, 0, 0)
            except:
                print ("    ERROR: Signal finishing")
        self.set_speed()
        self.finished = True

    def _win_handler(self):
        """
        Timer handler for Windows platform.
        """
        self.next_call+=self.sample_time
        #---- check for end the movement unavoidably ----
        if self.finished:
            self.action_exec()
            return
        threading.Timer(self.next_call - time.time(), self._win_handler).start()
        self._timer_handler()
    
    def _unix_handler(self, signum, frame):
        """
        Timer handler for UNIX or OS X platform.
        """
        #---- check for end the movement unavoidably ----
        if self.finished:
            self.action_exec()
            return
        self._timer_handler()

    def _timer_handler(self):
        """
        Timer handler that generate movement.
        """
        #---- calculate the speed for each wheel ----
        encoder1, encoder2, _ = self.get_state()
        delta_encoder_1, delta_encoder_2 = self.navigation(encoder1, encoder2)
        #---- displacement ----
        if self.motion=="move":
            #---- PID by software ----
            if not settings.PID:
                elapsed = pid.process_time()                        
                set_point1, set_point2 = self._tracking()
                set_point1, set_point2 = pid.speeds_regulation(set_point1, set_point2,
                                                               delta_encoder_1, delta_encoder_2,
                                                               elapsed, 0, 0, 0)
            #---- PID by hardware ----
            else:
                set_point1, set_point2 = self._tracking()
            #---- set calculated speeds ----
            self.set_speed(set_point1, set_point2)
            #---- condition of stop ----
            self.count += 1
            if self.count >= self.reference.n_points:
                self.finished = True
        #---- rotation ----
        elif self.motion=="rotate":
            if self.angle<0:
                self.set_speed(2, -2)
            else:
                self.set_speed(-2, 2)
            z_position=self.z_position-int(self.z_position/(2*math.pi))*2*math.pi
            tmp=abs(self.angle-z_position)
            if tmp<self.difference and tmp>0.1:
                self.difference=tmp
            else:
                self.finished = True
    
    def _unix_timer_start(self):
        """
        Start the timer in UNIX or OS X platform.
        """
        if not settings.PID:
            pid.config(time.time(),self.sample_time)
        try:
            signal.setitimer(signal.ITIMER_REAL, self.sample_time, self.sample_time)
        except:
            print("    ERROR: Signal starting")

    def _win_timer_start(self):
        """
        Start the timer in Windows platform.
        """
        self.next_call=time.time()
        self._win_handler()

    def _tracking(self):
        """
        Calculate the speed of each wheel according to the track.
        """
        xd = self.reference.xd_vector[self.count]
        xd_dot = self.reference.xd_dot_vector[self.count]
        yd = self.reference.yd_vector[self.count]
        yd_dot = self.reference.yd_dot_vector[self.count]
        zd = self.reference.zd_vector[self.count]
        zd_dot = self.reference.zd_dot_vector[self.count]

        y1 = self.x_position + settings.CONST_B * math.cos(self.z_position)
        y2 = self.y_position + settings.CONST_B * math.sin(self.z_position)

        if self.smooth:
            y1d = xd
            y2d = yd
            y2d_dot = yd_dot
            y1d_dot = xd_dot
        else:
            y1d = xd + settings.CONST_B * math.cos(zd)
            y2d = yd + settings.CONST_B * math.sin(zd)

            y2d_dot = yd_dot + settings.CONST_B * math.cos(zd) * zd_dot
            y1d_dot = xd_dot - settings.CONST_B * math.sin(zd) * zd_dot

        u2 = y2d_dot + settings.CONST_K2 * (y2d - y2)
        u1 = y1d_dot + settings.CONST_K1 * (y1d - y1)

        the_v = math.cos(self.z_position) * u1 + u2 * math.sin(self.z_position)
        the_omega = u1 * (- math.sin(self.z_position) / settings.CONST_B) + u2 * math.cos(
            self.z_position) / settings.CONST_B

        set_point2 = the_v / settings.RADIUS + the_omega * settings.DISTANCE / 2 / settings.RADIUS
        set_point1 = the_v / settings.RADIUS - the_omega * settings.DISTANCE / 2 / settings.RADIUS

        return set_point1, set_point2

    def navigation(self, encoder1, encoder2):
        """
        Calculate the current position of the robot.
        
        :param encoder1: value of encoder of the right wheel
        :type encoder1: float
        :param encoder2: value of encoder of the left wheel 
        :type encoder2: float
        :return: differential of the encoders
        :type: tuple
        
        >>> controller=Controller()        
        >>> controller.navigation(0.2,0.7)
        (0.15, 0.09)
        """
        #XXX fix the send position
        global COUNTER_POS
    
        delta_encoder_1 = encoder1 - self.prev_encoder1
        delta_encoder_2 = encoder2 - self.prev_encoder2

        self.encoder1 = encoder1
        self.encoder2 = encoder2

        if delta_encoder_1 > 130 or delta_encoder_1 < -130:
            delta_encoder_1 = self.prev_delta_encoder_1
            self.encoder1 = 0
            self.encoder2 = 0
            self.robot.reset_encoders()

        if delta_encoder_2 > 130 or delta_encoder_2 < -130:
            delta_encoder_2 = self.prev_delta_encoder_2
            self.encoder1 = 0
            self.encoder2 = 0
            self.robot.reset_encoders()

        if encoder1 > 2000000000 or encoder1 < -2000000000 or encoder2 > 2000000000 or encoder2 < -2000000000:
            self.encoder1 = 0
            self.encoder2 = 0
            self.robot.reset_encoders()

        self.prev_encoder1 = self.encoder1
        self.prev_encoder2 = self.encoder2

        self.prev_delta_encoder_1 = delta_encoder_1
        self.prev_delta_encoder_2 = delta_encoder_2
        dfr = delta_encoder_2 * 2 * math.pi / settings.ENCODER_STEPS
        dfl = delta_encoder_1 * 2 * math.pi / settings.ENCODER_STEPS

        ds = (dfr + dfl) * settings.RADIUS / 2
        dz = (dfr - dfl) * settings.RADIUS / settings.DISTANCE

        self.x_position += ds * math.cos(self.z_position + dz / 2)
        self.y_position += ds * math.sin(self.z_position + dz / 2)
        self.z_position += dz

        #log position
        if global_settings.LOG:
            self.log_file.write(datetime.now().time().isoformat()+" "+
                                str(-self.y_position)+" "+
                                str(self.x_position)+" "+
                                str(self.z_position)+"\n")
        #send position
        # self.COUNTER_POS+=1
        # if self.COUNTER_POS==3:
        self.SEND_POSITION(-self.y_position, self.x_position, self.z_position)
        self.COUNTER_POS=0;

        return delta_encoder_1, delta_encoder_2

    def action_exec(self):
        """
        Execute predefined actions for the robot.
        
        This function read and execute the actions defined in ``actions.py`` 
        
        >>> controller=Controller()
        >>> controller.action_exec()
        """
        try:
            importlib.import_module('robot.actions')
        except OSError:
            print("    ERROR: Actions")
            
    def async_speed(self,x,y):
        """
        calculate the wheel speeds for a asynchronous event.

        :param x: value of displacement in X axis
        :type x: float
        :param y: value of displacement in Y axis
        :type y: float        
        :return: wheel speeds
        :type: tuple
        
        >>> controller=Controller()        
        >>> controller.async_speed(0.5,0.8)
        (0.46, 0.8)
        """
        left=right=y
        ratio=abs(x/settings.MAX_SPEED)
        if x>0:
            right*=(1-ratio)
        elif x<0:
            left*=(1-ratio)
        return right, left
