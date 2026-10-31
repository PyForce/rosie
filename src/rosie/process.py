"""The robot's process: the robot, its control loop and its web API, until a signal."""

import asyncio
import logging
import signal
import time

from rosie import runner
from rosie.apis.web.server import serve
from rosie.models import Settings
from rosie.planning.maps import MAPS_DIR, list_maps
from rosie.profile import load_profile
from rosie.robot import Robot
from rosie.sensors import usound

logger = logging.getLogger(__name__)


async def run(settings: Settings) -> None:
    """Run the robot and its web API until a signal."""
    profile = load_profile(settings.robot)
    # the robot's own maps first: they win a name over rosie's
    robot = Robot(
        profile, list_maps([profile.maps, MAPS_DIR]), settings.map, settings.record, time.monotonic
    )
    if profile.usound:
        usound.attach(robot, profile.usound)

    # a flag, so a signal arriving twice (uvicorn re-raises the ones it handles) is harmless
    stopping = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signum, stopping.set)

    running = asyncio.create_task(runner.run(robot))
    web = asyncio.create_task(serve(robot, settings.host, settings.port))
    logger.info("web API on http://%s:%d", settings.host, settings.port)

    await stopping.wait()
    logger.info("stopping...")
    running.cancel()
    # the motors first, then the web API
    robot.stop()
    web.cancel()
    await asyncio.gather(running, web, return_exceptions=True)
    logger.info("stopped")
