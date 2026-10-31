import asyncio
import socket
import threading
import time
from collections.abc import Iterator

import pytest
import uvicorn

from rosie.apis.web.server import create_app
from rosie.client import Position, RobotInfo, RosieClient
from rosie.core import Robot
from rosie.errors import NoRouteError, RequestError
from rosie.models import Profile
from rosie.robot import build_robot
from rosie.service import start_control_loop
from rosie.world.maps import DEFAULT_MAP


@pytest.fixture
def served(simubot_profile: Profile) -> Iterator[tuple[RosieClient, Robot]]:
    """A real rosie, web API and control loop, on a free port in a background thread."""
    robot = build_robot(simubot_profile, DEFAULT_MAP, None, time.monotonic)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(create_app(robot), host="127.0.0.1", port=port, log_level="warning")
    )

    async def serve() -> None:
        async with start_control_loop(robot):
            await server.serve()

    thread = threading.Thread(target=asyncio.run, args=(serve(),))
    thread.start()
    while not server.started:
        time.sleep(0.01)
    yield RosieClient(f"http://127.0.0.1:{port}/"), robot
    server.should_exit = True
    thread.join()


def arrive(client: RosieClient, x: float, y: float) -> Position:
    # close enough to show the client works; the last centimetres are slow, and test_robot checks them
    deadline = time.monotonic() + 10
    for position in client.positions():
        if position.distance_to(x, y) < 0.05:
            return position
        assert time.monotonic() < deadline, f"still {position.distance_to(x, y):.2f} m away"
    raise AssertionError("the positions stopped")


def test_odometry_and_teleport(served: tuple[RosieClient, Robot]) -> None:
    client, _ = served
    assert client.odometry() == Position(0, 0, 0)
    client.teleport(1, 2, 0.5)
    assert client.odometry() == Position(1, 2, 0.5)


def test_metadata(served: tuple[RosieClient, Robot]) -> None:
    client, _ = served
    assert client.metadata() == RobotInfo(
        "SIMUBOT", "simubot", "/thumbnail", "/vector", None, (0.2, 0.42, 0.0)
    )


def test_goto_and_watch_it_arrive(served: tuple[RosieClient, Robot]) -> None:
    client, robot = served
    client.goto(0.5, 0.25, 0.5)
    arrive(client, 0.5, 0.25)
    assert Position(*robot.position()).distance_to(0.5, 0.25) < 0.05


def test_follow(served: tuple[RosieClient, Robot]) -> None:
    client, _ = served
    client.follow([(0.3, 0), (0.3, 0.3)], 0.5)
    arrive(client, 0.3, 0.3)


def test_planner(served: tuple[RosieClient, Robot]) -> None:
    client, _ = served
    client.teleport(1, 1, 0)
    with pytest.raises(NoRouteError, match="no route from"):
        client.goto_with_planner(5, 1, 0.5)
    client.goto_with_planner(1.5, 1.2, 0.8)
    arrive(client, 1.5, 1.2)


def test_impossible_orders(served: tuple[RosieClient, Robot]) -> None:
    client, _ = served
    with pytest.raises(ValueError, match="speed must be above 0"):
        client.goto(1, 0, 0)
    with pytest.raises(ValueError, match="speed must be above 0"):
        client.follow([(1, 0)], 5.0)


def test_maps(served: tuple[RosieClient, Robot]) -> None:
    client, _ = served
    assert client.maps() == [DEFAULT_MAP]
    assert client.map(DEFAULT_MAP) == client.current_map()
    features = client.current_map()["features"]
    rooms = {f["properties"]["name"] for f in features if f["properties"]["kind"] == "room"}
    assert rooms == {"Dinning Room", "Hall", "Kitchen", "Living Room"}
    client.use_map(DEFAULT_MAP)
    with pytest.raises(RequestError, match="404: no map Nowhere") as refused:
        client.use_map("Nowhere")
    assert refused.value.status == 404
    with pytest.raises(RequestError, match="404"):
        client.map("Nowhere")


def test_sensors(served: tuple[RosieClient, Robot]) -> None:
    client, robot = served
    robot.sensors["usound"] = lambda: [12.5, None]
    assert client.sensor("usound") == [12.5, None]
    with pytest.raises(RequestError, match="no sensor sonar"):
        client.sensor("sonar")


def test_drive_by_hand(served: tuple[RosieClient, Robot]) -> None:
    client, robot = served
    with client.drive() as wheel:
        wheel.move(steering=0.0, throttle=1.0, spin=0.0)
        time.sleep(0.5)
    stopped = robot.position()
    time.sleep(0.3)
    assert robot.position() == stopped  # stopped when the block ended
    assert stopped[0] > 0.1
    client.goto(0, 0, 0.5)  # planned movements again
    arrive(client, 0, 0)
