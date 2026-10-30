#! /usr/bin/env python
r"""
       ___  ____
  _ _ / _ \/ ___\ _
 | '_| | | \___ \(_)
 | | | |_| |___) | |
 |_|  \___/\____/|_|

"""

import argparse
import asyncio
import importlib
import logging
import signal
import traceback

from rosie.config import config

# config section -> module with `async def run(robot, settings)`
PLUGINS = {
    'web': 'rosie.apis.web.server',
    'usound': 'rosie.sensors.usound',
}

FORMAT = '[%(asctime)-15s] %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT,
                    level=getattr(logging, config.get(
                        'general', 'loglevel').upper(), None),
                    filename=config.get('general', 'logfile'))


def test(args):
    """
    Run rosie tests
    """
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


def start(args):
    """
    Handles the start of the rosie application
    """
    asyncio.run(run())


async def run():
    """
    Run the robot, and every active plugin next to it, until a signal
    """
    from rosie.robot import Robot
    from rosie import runner

    robot = Robot()

    # a flag, so a signal arriving twice (uvicorn re-raises the ones it
    # handles) is harmless
    stopping = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signum, stopping.set)

    running = asyncio.create_task(runner.run(robot))

    plugins = []
    for sect in (s for s in config.sections()
                 if config.getboolean(s, 'active')):
        logging.info('loading %s...', sect)
        if sect not in PLUGINS:
            logging.error('unknown section [%s], known: %s', sect,
                          ', '.join(PLUGINS))
            continue
        try:
            module = importlib.import_module(PLUGINS[sect])
        except ImportError:
            logging.error(traceback.format_exc())
            logging.error('module %s not loaded\033[0m', sect)
        # no exception was raised
        else:
            logging.info('loaded %s', sect)
            if hasattr(module, 'run'):
                task = asyncio.create_task(module.run(robot, config[sect]),
                                           name=sect)
                task.add_done_callback(report_plugin_end)
                plugins.append(task)

    await stopping.wait()
    logging.info('stopping...')
    running.cancel()
    # the motors first, then the plugins
    robot.stop()
    for task in plugins:
        task.cancel()
    await asyncio.gather(running, *plugins, return_exceptions=True)
    logging.info('stopped')


def report_plugin_end(task):
    """
    Log a plugin that ended with an error (the robot keeps running)
    """
    if not task.cancelled() and task.exception():
        logging.error('plugin %s failed', task.get_name(),
                      exc_info=task.exception())


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
