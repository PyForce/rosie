from abc import ABCMeta, abstractmethod


class AbstractTimer:
    """
    Abstract class to generate sample time of a mobile robot, or anything else

    """
    __metaclass__ = ABCMeta

    def __init__(self, sample_time):
        self.sample_time = sample_time
        self.timer_overflow = lambda: None


    def set_timer_overflow_function(self, func):
        self.timer_overflow = func

    @abstractmethod
    def timer_init(self):
        """
        Init the timer
        """
        pass


    @abstractmethod
    def timer_handler(self):
        """
        Handle the timer overflow
        """
        pass


    @abstractmethod
    def timer_stop(self):
        """
        Stop the timer
        """
        pass

