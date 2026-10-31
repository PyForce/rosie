import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Protocol


class Tickable(Protocol):
    @property
    def sample_time(self) -> float: ...

    def tick(self) -> None: ...


class Stoppable(Tickable, Protocol):
    def stop(self) -> None: ...


@asynccontextmanager
async def start_control_loop(robot: Stoppable) -> AsyncGenerator[None, None]:
    """Start the control loop; on the way out of the block, end it and stop the motors."""
    ticking = asyncio.create_task(run(robot))
    try:
        yield
    finally:
        ticking.cancel()
        robot.stop()
        await asyncio.gather(ticking, return_exceptions=True)


async def run(robot: Tickable) -> None:
    """Call `robot.tick()` every `robot.sample_time` seconds, until cancelled."""
    loop = asyncio.get_running_loop()
    deadline = loop.time()
    while True:
        robot.tick()
        deadline += robot.sample_time
        delay = deadline - loop.time()
        if delay < 0:
            # running late: keep the period, don't burst to catch up
            deadline = loop.time()
            delay = 0
        await asyncio.sleep(delay)
