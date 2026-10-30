"""
Runs the robot: one control step every sample time
"""
import asyncio


async def run(robot):
    """
    Call `robot.tick()` every `robot.sample_time` seconds, until cancelled
    """
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
