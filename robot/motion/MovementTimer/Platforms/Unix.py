from robot.motion.MovementTimer.Timer import AbstractTimer
import signal

__all__ = ['UnixTimer', 'DefaultTimer']


class UnixTimer(AbstractTimer):
    """
    Class to generate sample time for Unix Systems to drive a mobile robotOLD,
    or anything else
    """

    def __init__(self, sample_time):
        super(UnixTimer, self).__init__(sample_time)
        signal.signal(signal.SIGALRM, self.timer_handler)
        self.timer_stop()

    def timer_init(self):
        """
        Init the timer
        """
        signal.setitimer(signal.ITIMER_REAL, self.sample_time,
                         self.sample_time)

    def timer_handler(self, signum, frame):
        """
        Handle the timer overflow

        @param frame: Stack Frame
        @param signum: Signal number
        """
        self.timer_overflow()

    def timer_stop(self):
        """
        Stop the timer
        """
        signal.setitimer(signal.ITIMER_REAL, 0, 0)

DefaultTimer = UnixTimer
