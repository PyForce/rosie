import asyncio
import time

from rosie import runner


class Counter:
    sample_time = 0.01

    def __init__(self) -> None:
        self.ticks = 0

    def tick(self) -> None:
        self.ticks += 1


class Stopping(Counter):
    def __init__(self) -> None:
        super().__init__()
        self.stopped_after: int | None = None

    def stop(self) -> None:
        self.stopped_after = self.ticks


class Slow(Counter):
    def tick(self) -> None:
        super().tick()
        if self.ticks == 1:
            time.sleep(0.05)  # five periods late


async def run_for(robot: Counter, seconds: float) -> None:
    task = asyncio.create_task(runner.run(robot))
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


def test_control_loop_stops_the_motors_on_the_way_out() -> None:
    robot = Stopping()

    async def scenario() -> None:
        async with runner.start_control_loop(robot):
            await asyncio.sleep(0.05)
        ticks = robot.ticks
        await asyncio.sleep(0.05)
        assert robot.ticks == ticks  # no tick after the loop ended

    asyncio.run(scenario())
    assert robot.stopped_after is not None
    assert robot.stopped_after > 0
