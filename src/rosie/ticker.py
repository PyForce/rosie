import asyncio

from rosie.models import Tickable


async def keep_ticking(tickable: Tickable) -> None:
    """Call `tickable.tick()` every `tickable.sample_time` seconds, until cancelled."""
    loop = asyncio.get_running_loop()
    deadline = loop.time()
    while True:
        tickable.tick()
        deadline += tickable.sample_time
        delay = deadline - loop.time()
        if delay < 0:
            # running late: keep the period, don't burst to catch up
            deadline = loop.time()
            delay = 0
        await asyncio.sleep(delay)
