import sys

__all__ = []

if sys.platform == 'win32':
    # use windows timer as default timer
    from .Platforms.Windows import *
    __all__ += Platforms.Windows.__all__
else:
    # use unix timer as default timer
    from .Platforms.Unix import *
    __all__ += Platforms.Unix.__all__
