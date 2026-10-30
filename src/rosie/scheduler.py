import heapq
import functools
import threading


class Scheduler:
    def __init__(self):
        self.timed_events = []
        self.untimed_events = []
        self._mode = 'stack'

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        assert value == 'stack' or value == 'queue'
        self._mode = value

    def schedule(self, task):
        if task.start_time or task.stop_time:
            # insert into the tasks heaps
            heapq.heappush(self.timed_events, task)
        else:
            self.untimed_events.append(task)


@functools.total_ordering  # define the rest of the comparisson methods
class Task:
    def __init__(self, start_time=None, stop_time=None, target=None, args=None,
                 kwargs=None):
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.start_time = start_time
        self.stop_time = stop_time

    def __eq__(self, other):
        return self.start_time == other.start_time

    def __gt__(self, other):
        return self.start_time > other.start_time

    def run(self):
        """
            Use threading events to control interrupt request
            ```
            def task_target():
                while task_target.event.is_set():
                    ...
            ```
        """
        self.target.event = threading.Event()
        self.target.event.set()
        self.target(*self.arg, **self.kwargs)

    def end(self):
        self.target.event.clear()


if __name__ == '__main__':
    sch = Scheduler()

    def print_task():
        print('Hello World!!')
    t_print = Task(target=print_task)

    sch.schedule(t_print)
