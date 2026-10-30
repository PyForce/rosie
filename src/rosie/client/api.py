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

from rosie.client.models import Metadata, Position
from rosie.errors import NoRouteError, RequestError

logger = logging.getLogger(__name__)

TIMEOUT = 10.0  # s for a request to be answered

# steer (+1 right), throttle (+1 forward), rotation (+1 clockwise, like E), each in [-1, 1]
type Direction = tuple[float, float, float]


class Driver:
    """Manual control, inside RosieClient.drive()."""

    def __init__(self, websocket: ClientConnection) -> None:
        self.websocket = websocket

    def move(self, direction: Direction) -> None:
        """Keep moving this way until the next move: steer, throttle, rotation in [-1, 1]."""
        self.websocket.send(json.dumps({"type": "move", "data": list(direction)}))

    def stop(self) -> None:
        self.move((0.0, 0.0, 0.0))


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

    def metadata(self) -> Metadata:
        data = self._request("GET", "/metadata", None)
        return Metadata(
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

    def goto(self, x: float, y: float, t: float) -> None:
        """Drive straight to (x, y) in t seconds."""
        self._request("POST", "/goto", {"target": [x, y, t]})

    def goto_with_planner(self, x: float, y: float, t: float) -> None:
        """Drive to (x, y) around the walls and furniture of the map, t seconds per stretch."""
        self._request("POST", "/goto", {"target": [x, y, t], "planner": True})

    def follow(self, points: Sequence[tuple[float, float]], t: float) -> None:
        """Drive through the points in order, t seconds from one to the next."""
        self._request("POST", "/follow", {"path": [list(point) for point in points], "time": t})

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
                wheel.move((0, 1, 0))  # forward
                time.sleep(1)

        The robot stops, and planned movements are accepted again, when the block ends.
        """
        self._request("POST", "/manual_mode", None)
        try:
            with self._websocket() as websocket:
                driver = Driver(websocket)
                try:
                    yield driver
                finally:
                    driver.stop()
        finally:
            self._request("POST", "/auto_mode", None)

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
