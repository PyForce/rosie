# Web API and extensions

rosie's core knows nothing about networks: `rosie start` puts its **interfaces** next to it, the ones
`--interfaces` names (`web` by default, the REST + WebSocket API). The robot itself opens the sensors its
profile names, such as the ultrasound board.

## The web API

`apis/web/` · FastAPI, served by uvicorn on rosie's own event loop

It listens on `--host` and `--port` ([Configure it](getting-started.md#configure-it)).

The interactive documentation of every route is at `/docs` (for example <http://localhost:5000/docs>).

| Route | Does |
|---|---|
| `GET /odometry` | where the robot is: `{"x": 0.0, "y": 0.0, "theta": 0.0}` (m, m, rad) |
| `GET /metadata` | its name, profile, size, picture and icon paths, camera stream |
| `GET /thumbnail`, `GET /vector` | its picture and its icon |
| `POST /position` | tell it where it is (teleport): `{"x": 1, "y": 2, "theta": 0}` |
| `POST /goto` | `{"target": [x, y, t]}`: go to (x, y) in t s; add `"planner": true` to go around obstacles |
| `POST /follow` | `{"path": [[x, y], ...], "time": t}`: through the points, t s from one to the next |
| `GET /maps` | the maps it knows |
| `GET /map`, `GET /map/{name}` | the map in use, or another one (JSON) |
| `POST /map/{name}` | plan on that map from now on |
| `GET /sensor/{name}` | a sensor's reading, e.g. `/sensor/usound` |
| `POST /manual`, `POST /planned` | drive by hand, or go back to planned movements |
| `/websocket` | positions out, keys in (below) |

Errors: 422 for a malformed or impossible order (a time shorter than one control step), 409 when the planner
finds no route, 404 for an unknown map or sensor. Any web page may call the API (CORS is open), since
WebRosie may be served from elsewhere.

**WebSocket.** rosie sends every client the robot's position each time it changes:

```json
{"type": "position", "data": {"x": 0.5, "y": 0.2, "theta": 0.3}}
```

In manual mode, clients send the pressed keys, and the robot moves that way until the next message:

```json
{"type": "move", "data": [0, 1, 0]}
```

`data` is steer (+1 right), throttle (+1 forward) and rotation (+1 clockwise), each in $[-1, 1]$.

## WebRosie

[WebRosie](https://github.com/PyForce/WebRosie) is the web interface: a map with the robots on it, and the
modes described in [Getting started](getting-started.md#drive-the-robot). It is a static web page that talks
to one or more rosies through this API; the Docker image serves it together with rosie.

## The Python client

`pip install pyforce-rosie` and `from rosie.client import RosieClient`: see [Python client](client.md).

## The ultrasound board

`hardware/sensors/usound.py`

Twelve ultrasonic range sensors and an LM35 thermometer behind a microcontroller on the I2C bus. A robot
that has one says so in its `profile.toml`:

```toml
[sensors.usound]
bus = 1  # the default
address = 0x10  # the default
```

Its distances (cm, corrected for the sensors' error) are at `GET /sensor/usound`.

## Extending rosie

Your code gets the `Robot`, in a script or a notebook of your own ([simulate faster than real
time](getting-started.md#simulate-faster-than-real-time)). From there it can:

- **add a sensor**: `robot.sensors["name"] = read`, a function returning the reading; the web API serves it at
  `/sensor/name`. For a sensor that profiles can name, write a function from its profile table to that
  reading function (like `open_sensor` in `hardware/sensors/usound.py`) and add it to `SENSORS` in `hardware/sensors/__init__.py`;
- **follow every movement**: write a class with the three methods of `MovementSupervisor`
  (`movement_begin`, `movement_update`, `movement_end`; no base class needed) and
  `robot.supervisors.append(...)` it; `movement_update` gets the full `RobotState` of each
  control step. The web API and the recorder are both supervisors;
- **give orders**: anything `Robot` offers, such as `goto`, `follow` or `position`.
