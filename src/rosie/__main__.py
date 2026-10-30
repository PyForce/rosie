r"""
      ___  ____
 _ _ / _ \/ ___\ _
| '_| | | \___ \(_)
| | | |_| |___) | |
|_|  \___/\____/|_|

"""

import argparse
import asyncio
import configparser
import importlib
import logging
import signal
import time
from pathlib import Path

from rosie import runner
from rosie.config import load_config
from rosie.planning.maps import DEFAULT_MAP, MAPS_DIR, list_maps
from rosie.profile import PROFILES_DIR, load_profile
from rosie.robot import Robot

logger = logging.getLogger(__name__)

# config section -> module with `async def run(robot, settings)`
PLUGINS = {"web": "rosie.apis.web.server", "usound": "rosie.sensors.usound"}

LOG_FORMAT = "[%(asctime)-15s] %(levelname)s %(message)s"


def main() -> None:
    parser = argparse.ArgumentParser(prog="rosie", description="Modular robot control system")
    parser.add_argument("--config", type=Path, default=Path("config.ini"), help="INI file to use")
    subparsers = parser.add_subparsers(title="subcommands", required=True)
    subparsers.add_parser("start", help="start the robot and its active plugins")
    args = parser.parse_args()

    config = load_config(args.config)
    logging.basicConfig(
        format=LOG_FORMAT,
        level=config.get("general", "loglevel", fallback="INFO").upper(),
        filename=config.get("general", "logfile", fallback=None),
    )
    asyncio.run(run(config))


async def run(config: configparser.ConfigParser) -> None:
    """Run the robot, and every active plugin next to it, until a signal."""
    robot = Robot(
        load_profile(
            config.get("general", "profile", fallback="simubot"),
            _search(config, "profiles", PROFILES_DIR),
        ),
        list_maps(_search(config, "maps", MAPS_DIR)),
        config.get("general", "map", fallback=DEFAULT_MAP),
        _optional_path(config.get("recording", "directory", fallback=None)),
        time.monotonic,
    )

    # a flag, so a signal arriving twice (uvicorn re-raises the ones it handles) is harmless
    stopping = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signum, stopping.set)

    running = asyncio.create_task(runner.run(robot))
    plugins = [
        task for section in config.sections() if (task := _start_plugin(robot, config, section))
    ]

    await stopping.wait()
    logger.info("stopping...")
    running.cancel()
    # the motors first, then the plugins
    robot.stop()
    for task in plugins:
        task.cancel()
    await asyncio.gather(running, *plugins, return_exceptions=True)
    logger.info("stopped")


def _search(config: configparser.ConfigParser, option: str, builtin: Path) -> list[Path]:
    """The user's folder for `option` (from [general]), if any, then rosie's own."""
    user = _optional_path(config.get("general", option, fallback=None))
    return [user, builtin] if user else [builtin]


def _optional_path(value: str | None) -> Path | None:
    return Path(value).expanduser() if value else None


def _start_plugin(
    robot: Robot, config: configparser.ConfigParser, section: str
) -> asyncio.Task[None] | None:
    if not config.getboolean(section, "active", fallback=False):
        return None
    if section not in PLUGINS:
        logger.error("unknown section [%s], known: %s", section, ", ".join(PLUGINS))
        return None
    try:
        module = importlib.import_module(PLUGINS[section])
    except ImportError:
        logger.exception("plugin %s not loaded", section)
        return None
    logger.info("loaded %s", section)
    task = asyncio.create_task(module.run(robot, config[section]), name=section)
    task.add_done_callback(_report_plugin_end)
    return task


def _report_plugin_end(task: asyncio.Task[None]) -> None:
    """Log a plugin that ended with an error (the robot keeps running)."""
    if not task.cancelled() and (error := task.exception()):
        logger.error("plugin %s failed", task.get_name(), exc_info=error)


if __name__ == "__main__":
    main()
