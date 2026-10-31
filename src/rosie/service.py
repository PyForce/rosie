import asyncio
import logging
import signal
import time
from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager

from rosie.apis.web.server import start_web_api
from rosie.models import Settings
from rosie.planning.maps import MAPS_DIR, list_maps
from rosie.profile import load_profile
from rosie.robot import Robot
from rosie.runner import start_control_loop

logger = logging.getLogger(__name__)

# an interface serves the robot while inside its context
type Interface = Callable[[Robot, Settings], AbstractAsyncContextManager[None]]


async def run(settings: Settings) -> None:
    interfaces = choose_interfaces(settings.interfaces)
    robot = build_robot(settings)
    stop = stop_signal()
    # leaving the block stops the control loop (and the motors) first, then the interfaces
    async with start_interfaces(robot, settings, interfaces), start_control_loop(robot):
        await stop.wait()
        logger.info("stopping...")
    logger.info("stopped")


def choose_interfaces(names: tuple[str, ...]) -> list[Interface]:
    if any(name not in INTERFACES for name in names):
        raise ValueError(
            f"unsupported interfaces: {', '.join(names)} (known: {', '.join(INTERFACES)})"
        )
    return [INTERFACES[name] for name in names]


def build_robot(settings: Settings) -> Robot:
    profile = load_profile(settings.robot)
    # the robot's own maps first: they win a name over rosie's
    maps = list_maps([profile.maps, MAPS_DIR])
    return Robot(profile, maps, settings.map, settings.record, time.monotonic)


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


INTERFACES: dict[str, Interface] = {"web": start_web_api}
