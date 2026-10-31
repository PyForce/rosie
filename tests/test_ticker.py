import asyncio
import time

from rosie.ticker import keep_ticking


class Counter:
    sample_time = 0.01

    def __init__(self) -> None:
        self.ticks = 0

    def tick(self) -> None:
        self.ticks += 1


class Slow(Counter):
    def tick(self) -> None:
        super().tick()
        if self.ticks == 1:
            time.sleep(0.05)  # five periods late


async def run_for(robot: Counter, seconds: float) -> None:
    task = asyncio.create_task(keep_ticking(robot))
    await asyncio.sleep(seconds)
    task.cancel()


def test_ticks_every_sample_time() -> None:
    robot = Counter()
    asyncio.run(run_for(robot, 0.1))
    assert 8 <= robot.ticks <= 12


def test_doesnt_burst_after_running_late() -> None:
    robot = Slow()
    asyncio.run(run_for(robot, 0.1))
    assert robot.ticks <= 8  # 0.05 s lost, the rest at the normal pace
