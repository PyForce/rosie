import asyncio
import logging
import signal
import time
from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager

from rosie.apis.web.server import start_web_api
from rosie.core import Robot
from rosie.errors import SetupError
from rosie.models import Interface, Settings
from rosie.profile import load_profile
from rosie.robot import build_robot
from rosie.ticker import keep_ticking

logger = logging.getLogger(__name__)


async def run(settings: Settings) -> None:
    interfaces = choose_interfaces(settings.interfaces)
    robot = build_robot(
        load_profile(settings.profile), settings.map, settings.record, time.monotonic
    )
    stop = stop_signal()
    # leaving the block stops the control loop (and the motors) first, then the interfaces
    async with start_interfaces(robot, settings, interfaces), start_control_loop(robot):
        await stop.wait()
        logger.info("stopping...")
    logger.info("stopped")


def choose_interfaces(names: tuple[str, ...]) -> list[Interface]:
    if any(name not in INTERFACES for name in names):
        raise SetupError(
            f"unsupported interfaces: {', '.join(names)} (known: {', '.join(INTERFACES)})"
        )
    return [INTERFACES[name] for name in names]


def stop_signal() -> asyncio.Event:
    # Set on SIGINT or SIGTERM; installed before uvicorn starts, which re-raises the ones it handles
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signum, stop.set)
    return stop


@asynccontextmanager
async def start_interfaces(
    robot: Robot, settings: Settings, interfaces: list[Interface]
) -> AsyncGenerator[None, None]:
    """Start every interface; on the way out of the block, close them, the last one first."""
    async with AsyncExitStack() as stack:
        for interface in interfaces:
            await stack.enter_async_context(interface(robot, settings))
        yield


@asynccontextmanager
async def start_control_loop(robot: Robot) -> AsyncGenerator[None, None]:
    """Start the control loop; on the way out of the block, end it and stop the motors."""
    ticking = asyncio.create_task(keep_ticking(robot))
    try:
        yield
    finally:
        ticking.cancel()
        robot.stop()
        await asyncio.gather(ticking, return_exceptions=True)


INTERFACES: dict[str, Interface] = {"web": start_web_api}
