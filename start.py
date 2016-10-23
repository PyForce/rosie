#! /usr/bin/env python
print("       ___  ____     ")
print("  _ _ / _ \/ ___\ _  ")
print(" | '_| | | \___ \(_) ")
print(" | | | |_| |___) | | ")
print(" |_|  \___/\____/|_| ")
print(" ------ SYSTEM ----- ")
print("")

import importlib
import os
import signal
import sys
import threading
import traceback

from modules import kernel
from settings import config
from robot import Robot

# allows for all modules to be imported as `import <module_name>`
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'modules')))


if __name__ == '__main__':
    # create the robot
    Robot()
    modules = []

    def close_modules(signum, frame):
        for module, thr in modules:
            print('[.] closing %s...' % module.__name__)
            if hasattr(module, 'end'):
                module.end()
            while thr and thr.isAlive():
                thr.join(3)
                if thr.is_alive():
                    print('\033[33m[*] join timed out, killing thread!!\033[0m')
                    if sys.version_info.major == 3:
                        thr._stop()
                    else:
                        thr._Thread__stop()
            print('[+] closed %s...' % module.__name__)
        event.clear()

    signal.signal(signal.SIGTERM, close_modules)
    signal.signal(signal.SIGINT, close_modules)

    for sect in filter(lambda s: config.getboolean(s, 'active'),
                       config.sections()):
        print('[.] loading %s...' % sect)
        try:
            module = importlib.import_module(sect)
        except Exception as e:
            traceback.print_exc()
            print('\033[31m[*] module %s not loaded\033[0m' % sect)
        # no exception was raised
        else:
            print('[+] loaded %s' % sect)
            thr = None
            if hasattr(module, 'init'):
                thr = threading.Thread(target=module.init)
                thr.start()
            modules.append((module, thr))

    # run kernel as main thread
    event = threading.Event()
    event.set()
    kernel._run(event)
