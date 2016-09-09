from robotNew.motion.MovementTimer.Timer import AbstractTimer

import time
import threading

class WindowsTimer(AbstractTimer):
    """
    Class to generate sample time for Windows Systems to drive a mobile robot, or anything else
    """

    def __init__(self, sample_time):
        super(WindowsTimer, self).__init__(sample_time)
        self.next_call=0
        self.end_timer=False
        self.timer_stop()

    def timer_init(self):
        """
        Init the timer
        """
        self.end_timer=False
        self.next_call=time.time()
        self.timer_handler()

    def timer_handler(self):
        """
        Handle the timer overflow
        """
        if self.end_timer:
            return
        self.next_call+=self.sample_time
        threading.Timer(self.next_call - time.time(), self.timer_handler).start()
        self.timer_overflow()

    def timer_stop(self):
        """
        Stop the timer
        """
        self.end_timer=True