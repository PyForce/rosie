import json
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from conftest import FakeClock
from rosie.apis.web.server import create_app
from rosie.const import MAP
from rosie.robot import Robot

HOUSE = MAP.default  # rosie's own map


@pytest.fixture
def client(robot: Robot) -> Iterator[TestClient]:
    with TestClient(create_app(robot)) as client:
        yield client


def tick(client: TestClient, robot: Robot, clock: FakeClock, seconds: float) -> None:
    """Run the robot inside the app's event loop, where the WebSocket sends live."""
    for _ in range(round(seconds / 0.05)):
        clock.now += 0.05
        client.portal.call(robot.tick)  # type: ignore[union-attr]


def test_odometry(client: TestClient, robot: Robot) -> None:
    robot.teleport(1, 2, 0.5)
    assert client.get("/odometry").json() == {"x": 1, "y": 2, "theta": 0.5}


def test_metadata(client: TestClient) -> None:
    metadata = client.get("/metadata").json()
    assert metadata["name"] == "SIMUBOT"
    assert metadata["profile"] == "simubot"
    assert (metadata["thumbnail"], metadata["vector"]) == ("/thumbnail", "/vector")
    assert metadata["video"] is False
    assert client.get(metadata["thumbnail"]).headers["content-type"] == "image/png"
    assert client.get(metadata["vector"]).headers["content-type"].startswith("image/svg")


def test_position_teleports(client: TestClient, robot: Robot) -> None:
    assert client.post("/position", content='{"x": 0.5, "y": 1, "theta": 0}').status_code == 200
    assert robot.position() == (0.5, 1, 0)


def test_goto(client: TestClient, robot: Robot, clock: FakeClock) -> None:
    assert client.post("/goto", content='{"target": [1, 0.5, 4]}').status_code == 200
    tick(client, robot, clock, 5)
    x, y, _ = robot.position()
    assert (x, y) == pytest.approx((1, 0.5), abs=0.01)


def test_goto_with_the_planner(client: TestClient, robot: Robot, clock: FakeClock) -> None:
    robot.teleport(1, 1, 0)
    assert (
        client.post("/goto", content='{"target": [7.7, 1.2, 3], "planner": true}').status_code
        == 200
    )
    tick(client, robot, clock, 30)
    x, y, _ = robot.position()
    assert (x, y) == pytest.approx((7.7, 1.2), abs=0.01)


def test_goto_without_a_route(client: TestClient, robot: Robot) -> None:
    robot.teleport(1, 1, 0)
    response = client.post("/goto", content='{"target": [5, 1, 3], "planner": true}')
    assert response.status_code == 409
    assert "not found" in response.json()["error"]


@pytest.mark.parametrize(
    ("route", "body"),
    [("/goto", '{"target": [1, 0, 0]}'), ("/follow", '{"path": [[1, 0]], "time": 0}')],
)
def test_too_short_times(client: TestClient, route: str, body: str) -> None:
    response = client.post(route, content=body)
    assert response.status_code == 422
    assert "control step" in response.json()["detail"]


@pytest.mark.parametrize(
    ("route", "body"),
    [
        ("/goto", "not json"),
        ("/goto", '{"target": [1, 0]}'),
        ("/follow", '{"path": [[1, 0]]}'),
        ("/position", '{"x": "far"}'),
    ],
)
def test_malformed_requests(client: TestClient, route: str, body: str) -> None:
    response = client.post(route, content=body)
    assert response.status_code == 422
    assert response.json()["detail"]


def test_follow(client: TestClient, robot: Robot, clock: FakeClock) -> None:
    assert (
        client.post("/follow", content='{"path": [[1, 0], [1, 1]], "time": 3}').status_code == 200
    )
    tick(client, robot, clock, 8)  # 3 s per segment
    x, y, _ = robot.position()
    assert (x, y) == pytest.approx((1, 1), abs=0.01)


def test_maps(client: TestClient) -> None:
    assert client.get("/maps").json() == {"maps": [HOUSE]}
    assert client.get("/map").json() == client.get(f"/map/{HOUSE}").json()
    assert client.get("/map/Nowhere").status_code == 404
    assert client.post(f"/map/{HOUSE}").status_code == 200
    assert client.post("/map/Nowhere").status_code == 404


def test_sensors(client: TestClient, robot: Robot) -> None:
    assert client.get("/sensor/usound").status_code == 404
    robot.sensors["usound"] = lambda: [12.5, None]
    assert client.get("/sensor/usound").json() == {"usound": [12.5, None]}


def test_cors(client: TestClient) -> None:
    response = client.get("/odometry", headers={"Origin": "http://elsewhere"})
    assert response.headers["access-control-allow-origin"] == "*"


def test_websocket_streams_positions(client: TestClient, robot: Robot, clock: FakeClock) -> None:
    with client.websocket_connect("/websocket") as websocket:
        client.post("/goto", content='{"target": [1, 0, 2]}')
        tick(client, robot, clock, 0.1)
        message = websocket.receive_json()
    assert message["type"] == "position"
    assert message["data"]["x"] > 0


def test_websocket_drives_in_manual_mode(
    client: TestClient, robot: Robot, clock: FakeClock
) -> None:
    move = json.dumps({"type": "move", "data": [0, 1, 0]})
    with client.websocket_connect("/websocket") as websocket:
        websocket.send_text(move)  # ignored: not in manual mode
        websocket.send_text('{"type": "move", "data": "fast"}')  # ignored: malformed
        websocket.send_text("[1, 2]")  # ignored: not a message
        tick(client, robot, clock, 0.5)
        assert robot.position() == (0, 0, 0)

        assert client.post("/manual_mode").status_code == 200
        websocket.send_text(move)
        websocket.send_text('{"type": "move", "data": "fast"}')
        tick(client, robot, clock, 0.05)  # lets the server read the messages
        tick(client, robot, clock, 1)
        assert robot.position()[0] > 0.2

        assert client.put("/auto_mode").status_code == 200
        before = robot.position()
        tick(client, robot, clock, 1)
        assert robot.position() == before
