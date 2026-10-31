<div align="center">

<img src="assets/logo.svg" alt="" width="96">

# rosie

**Mobile robots, in Python you can read**

[![QA](https://github.com/PyForce/rosie/actions/workflows/qa.yml/badge.svg)](https://github.com/PyForce/rosie/actions/workflows/qa.yml)
[![Release](https://img.shields.io/github/v/release/PyForce/rosie?label=release)](https://github.com/PyForce/rosie/releases/latest)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
<br>
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

<!-- Badges to move into the rows above once they apply:
[![PyPI](https://img.shields.io/pypi/v/pyforce-rosie)](https://pypi.org/project/pyforce-rosie/)
[![Docker image](https://img.shields.io/badge/docker-ghcr.io-2496ED?logo=docker&logoColor=white)](https://github.com/PyForce/rosie/pkgs/container/rosie)
[![Docs](https://readthedocs.org/projects/rosie/badge/?version=latest)](https://rosie.readthedocs.io)
-->

[Quick start](#quick-start) · [What you can learn](#what-you-can-learn) · [Documentation](#documentation) · [Development](#development)

</div>

---

rosie controls differential-drive mobile robots, the two-wheeled kind found in most robotics courses. It
estimates where the robot is from its wheel encoders, plans trajectories, tracks them with a feedback
controller, finds routes around walls and furniture, and lets you drive by hand from a browser or from
Python. Each of those is a short, plain Python module: open it, change it, test it on the simulated robot,
then run it on a real one.

It's made for learning and teaching robotics, from the control equations to the web page that drives the
robot.

## Quick start

rosie runs next to the robot, or next to a simulated one, and takes orders over a web API. There are
several ways to use it: from a browser, from Python, from plain HTTP, or by changing rosie itself. Each
one below starts with the simulated robot, so no hardware is needed.

### In the browser

```bash
docker run -p 8080:8080 ghcr.io/pyforce/rosie
```

Open <http://localhost:8080>: [WebRosie](https://github.com/PyForce/WebRosie), with a simulated robot in a
house. Click the map to send it somewhere, or drive it with the keyboard.

### As a Python package

```bash
pip install "pyforce-rosie[robot]"
rosie start
```

This runs rosie's web API on port 5000, without the web interface. Flags or `ROSIE_*` environment
variables pick another robot, map or port.

### From a Python script or notebook

With rosie running (either way above), on the same computer or any other:

```python
import time

from rosie.client import RosieClient  # pip install pyforce-rosie

robot = RosieClient("http://localhost:8080")  # 5000 with rosie start
print(robot.odometry())  # Position(x=0.0, y=0.0, theta=0.0)
robot.goto(1, 0.5, 4)  # to (1 m, 0.5 m) in 4 s
time.sleep(5)
print(robot.odometry())  # about Position(x=1.0, y=0.5, theta=0.46)
```

### Over HTTP

The web API is plain HTTP and JSON, so any language or tool can drive the robot:

```bash
curl -X POST localhost:8080/goto -d '{"target": [1, 0.5, 4]}'
curl localhost:8080/odometry
```

### From the source

To change rosie itself, for example to try your own controller:

```bash
git clone https://github.com/PyForce/rosie
cd rosie
uv sync
uv run rosie start
```

[Getting started](docs/getting-started.md) covers each of these in more detail, plus configuration.

## What you can learn

| Topic | In rosie |
|---|---|
| Wheel odometry | second-order Runge-Kutta, from encoder counts |
| Trajectory generation | straight lines, or cubic polynomials that round the corners |
| Trajectory tracking | input-output linearization; plug in your own controller as one class |
| Reaching a point | a polar go-to-point controller |
| Wheel speed control | an incremental PID |
| Route planning | free space, a visibility graph, A* |
| Hardware | serial and I2C motor boards, an ultrasound sensor board |
| Integration | a REST + WebSocket API, a web interface, a Python client |

The simulated robot runs on a clock you control, so a script can simulate a 10-second movement in
milliseconds, the same every time. Every planned movement can be recorded to CSV, one row per control step,
ready for pandas.

## Documentation

- [Getting started](docs/getting-started.md): running, driving and configuring rosie.
- [How rosie works](docs/how-rosie-works.md): the control loop, and where everything lives.
- [Motion control](docs/motion-control.md) and [Navigation](docs/navigation.md): the algorithms, with their
  equations.
- [Teaching with rosie](docs/teaching.md): lab ideas.
- [Robots and hardware](docs/robots.md), [Web API and extensions](docs/integration.md),
  [Python client](docs/client.md).

## Development

Setup, QA, docs and releases: [DEVELOPMENT.md](DEVELOPMENT.md).

## Contributing

Issues and pull requests are welcome; `make qa` must pass.

## License

MIT: see [LICENSE](LICENSE). rosie is a [PyForce](https://github.com/PyForce) project, started in 2015:
[authors](docs/about.md).

---

<sub>🚀 Project starter provided by [Cookie Pyrate v1.1.0](https://github.com/gvieralopez/cookie-pyrate/tree/v1.1.0)</sub>
