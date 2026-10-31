import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from http import HTTPStatus
from typing import Any

from websockets.sync.client import ClientConnection, connect

from rosie.client.models import Position, RobotInfo
from rosie.errors import NoRouteError, RequestError

logger = logging.getLogger(__name__)

TIMEOUT = 10.0  # s for a request to be answered


class Driver:
    """Manual control, inside RosieClient.drive()."""

    def __init__(self, websocket: ClientConnection) -> None:
        self.websocket = websocket

    def move(self, steering: float, throttle: float, spin: float) -> None:
        """
        Keep moving this way until the next move, each command in [-1, 1]: steering
        (+1 right), throttle (+1 forward), spin (+1 clockwise, on the spot).
        """
        self.websocket.send(json.dumps({"type": "move", "data": [steering, throttle, spin]}))

    def stop(self) -> None:
        self.move(steering=0.0, throttle=0.0, spin=0.0)


class RosieClient:
    """
    A robot running rosie with its web API. Orders raise what the robot
    itself would: NoRouteError when the planner can't get there,
    ValueError for impossible orders, RequestError for anything else.
    """

    def __init__(self, url: str) -> None:
        self.url = url.rstrip("/")

    def odometry(self) -> Position:
        data = self._request("GET", "/odometry", None)
        return Position(data["x"], data["y"], data["theta"])

    def metadata(self) -> RobotInfo:
        data = self._request("GET", "/metadata", None)
        return RobotInfo(
            data["name"],
            data["profile"],
            data["thumbnail"],
            data["vector"],
            data["video"] or None,
            tuple(data["size"]),
        )

    def sensor(self, name: str) -> object:
        return self._request("GET", f"/sensor/{_quote(name)}", None)[name]

    def teleport(self, x: float, y: float, theta: float) -> None:
        """Tell the robot it is somewhere else, without moving it."""
        self._request("POST", "/position", {"x": x, "y": y, "theta": theta})

    def goto(self, x: float, y: float, speed: float) -> None:
        """Drive straight to (x, y), at speed (m/s)."""
        self._request("POST", "/goto", {"target": [x, y], "speed": speed})

    def goto_with_planner(self, x: float, y: float, speed: float) -> None:
        """Drive to (x, y) around the walls and furniture of the map, at speed (m/s)."""
        self._request("POST", "/goto", {"target": [x, y], "speed": speed, "planner": True})

    def follow(self, points: Sequence[tuple[float, float]], speed: float) -> None:
        """Drive through the points in order, at speed (m/s)."""
        self._request(
            "POST", "/follow", {"path": [list(point) for point in points], "speed": speed}
        )

    def follow_with_planner(self, points: Sequence[tuple[float, float]], speed: float) -> None:
        """Drive through the points in order, around walls and furniture, at speed (m/s)."""
        path = [list(point) for point in points]
        self._request("POST", "/follow", {"path": path, "speed": speed, "planner": True})

    def trajectory_planners(self) -> tuple[list[str], str]:
        """The trajectory planners the robot knows, and the one it uses."""
        data = self._request("GET", "/trajectory-planners", None)
        return list(data["planners"]), str(data["in_use"])

    def use_trajectory_planner(self, name: str) -> None:
        """Plan the next movements with this trajectory planner (linear or cubic)."""
        self._request("POST", f"/trajectory-planner/{_quote(name)}", None)

    def maps(self) -> list[str]:
        maps: list[str] = self._request("GET", "/maps", None)["maps"]
        return maps

    def map(self, name: str) -> dict[str, Any]:
        worldmap: dict[str, Any] = self._request("GET", f"/map/{_quote(name)}", None)
        return worldmap

    def current_map(self) -> dict[str, Any]:
        """The map the planner uses."""
        worldmap: dict[str, Any] = self._request("GET", "/map", None)
        return worldmap

    def use_map(self, name: str) -> None:
        """Plan routes on this map from now on."""
        self._request("POST", f"/map/{_quote(name)}", None)

    def positions(self) -> Iterator[Position]:
        """Where the robot is, every time it moves (until you stop iterating)."""
        with self._websocket() as websocket:
            for text in websocket:
                message = json.loads(text)
                if message.get("type") == "position":
                    data = message["data"]
                    yield Position(data["x"], data["y"], data["theta"])

    @contextmanager
    def drive(self) -> Iterator[Driver]:
        """
        Drive by hand, as with WebRosie's keys:

            with robot.drive() as wheel:
                wheel.move(steering=0, throttle=1, spin=0)  # forward
                time.sleep(1)

        The robot stops, and planned movements are accepted again, when the block ends.
        """
        self._request("POST", "/manual", None)
        try:
            with self._websocket() as websocket:
                driver = Driver(websocket)
                try:
                    yield driver
                finally:
                    driver.stop()
        finally:
            self._request("POST", "/planned", None)

    def _websocket(self) -> ClientConnection:
        address = urllib.parse.urlsplit(self.url)
        scheme = "wss" if address.scheme == "https" else "ws"
        return connect(
            address._replace(scheme=scheme).geturl() + "/websocket", open_timeout=TIMEOUT
        )

    def _request(self, method: str, path: str, body: dict[str, Any] | None) -> Any:
        request = urllib.request.Request(  # noqa: S310 (the URL is the robot's, given by the user)
            self.url + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
                text = response.read().decode()
        except urllib.error.HTTPError as error:
            raise _refusal(error) from error
        return json.loads(text) if text else None


def _refusal(error: urllib.error.HTTPError) -> Exception:
    text = error.read().decode()
    try:
        data = json.loads(text)
    except ValueError:
        data = {}
    detail = str(data.get("error") or data.get("detail") or text or error.reason)
    if error.code == HTTPStatus.CONFLICT:
        return NoRouteError(detail)
    if error.code == HTTPStatus.UNPROCESSABLE_ENTITY:
        return ValueError(detail)
    return RequestError(error.code, detail)


def _quote(name: str) -> str:
    return urllib.parse.quote(name, safe="")
