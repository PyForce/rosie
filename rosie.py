#! /usr/bin/env python
print("       ___  ____     ")
print("  _ _ / _ \/ ___\ _  ")
print(" | '_| | | \___ \(_) ")
print(" | | | |_| |___) | | ")
print(" |_|  \___/\____/|_| ")
print(" ------ SYSTEM ----- ")
print("")

import argparse
import importlib
import logging
import os
import signal
import sys
import threading
import traceback

from settings import config

FORMAT = '[%(asctime)-15s] %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, filename='rosie.log')


# allows for all modules to be imported as `import <module_name>`
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'modules')))


def test(args):
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


def start(args):
    """
    Handles the start of the rosie application
    """
    from modules import kernel
    from robot import Robot
    # create the robot
    Robot()
    modules = []

    def close_modules(signum, frame):
        for module, thr in modules:
            logging.info('closing %s...', module.__name__)
            if hasattr(module, 'end'):
                module.end()
            while thr and thr.isAlive():
                thr.join(3)
                if thr.is_alive():
                    logging.warning(
                        '\033[33m join timed out, killing thread!!\033[0m')
                    if sys.version_info.major == 3:
                        thr._stop()
                    else:
                        thr._Thread__stop()
            logging.info('closed %s...', module.__name__)
        event.clear()

    signal.signal(signal.SIGTERM, close_modules)
    signal.signal(signal.SIGINT, close_modules)

    for sect in filter(lambda s: config.getboolean(s, 'active'),
                       config.sections()):
        logging.info('loading %s...' % sect)
        try:
            module = importlib.import_module(sect)
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error('\033[31m[*] module %s not loaded\033[0m', sect)
        # no exception was raised
        else:
            logging.info('loaded %s', sect)
            thr = None
            if hasattr(module, 'init'):
                thr = threading.Thread(target=module.init)
                thr.start()
            modules.append((module, thr))

    # run kernel as main thread
    event = threading.Event()
    event.set()
    kernel._run(event)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands')

    parser_test = subparsers.add_parser('test', help='run tests')
    parser_test.set_defaults(func=test)
    parser_start = subparsers.add_parser(
        'start', help='start the rosie application')
    parser_start.set_defaults(func=start)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
