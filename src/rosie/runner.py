import asyncio
from typing import Protocol


class Tickable(Protocol):
    @property
    def sample_time(self) -> float: ...

    def tick(self) -> None: ...


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
