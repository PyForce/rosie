#! /usr/bin/env python
import importlib
import os
import signal
import sys

from settings import config


# allows for all modules to be imported as `import <module_name>`
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'modules')))

print("       ___  ____     ")
print("  _ _ / _ \/ ___\ _  ")
print(" | '_| | | \___ \(_) ")
print(" | | | |_| |___) | | ")
print(" |_|  \___/\____/|_| ")
print(" ------ SYSTEM ----- ")
print("")

if __name__ == '__main__':
    modules = []

    def close_modules(signum, frame):
        for module in modules:
            if hasattr(module, 'end'):
                module.end()
    signal.signal(signal.SIGTERM, close_modules)
    signal.signal(signal.SIGINT, close_modules)

    for sect in filter(lambda s: config.getboolean(s, 'active'),
                       config.sections()):
        print('[.] loading %s...' % sect)
        try:
            module = importlib.import_module(sect)
        except Exception as e:
            print(e)
            print('\033[31m[*] module %s not loaded\033[0m' % sect)
        # no exception was raised
        else:
            print('[-] loaded %s' % sect)
            modules.append(module)
            if hasattr(module, 'init'):
                module.init()
