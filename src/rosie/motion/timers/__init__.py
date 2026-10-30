import sys

__all__ = []

if sys.platform == 'win32':
    # use windows timer as default timer
    from rosie.motion.timers.windows import *
    __all__ += windows.__all__
else:
    # use unix timer as default timer
    from rosie.motion.timers.unix import *
    __all__ += unix.__all__
