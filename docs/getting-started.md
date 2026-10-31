# Getting started

## Run it

=== "Docker"

    ```bash
    docker run -p 8080:8080 ghcr.io/pyforce/rosie
    ```

    Open <http://localhost:8080>. The image holds rosie, WebRosie and a small web server in front of both;
    the page adds its simulated robot by itself.

=== "pip"

    ```bash
    pip install "pyforce-rosie[robot]"
    rosie start
    ```

    The first start writes a `config.ini` in the current folder: the simulated robot, with its web API on
    port 5000. Plain `pip install pyforce-rosie`, without `[robot]`, is the [Python client](client.md)
    alone, for computers that only talk to a robot.

=== "From the source"

    ```bash
    git clone https://github.com/PyForce/rosie
    cd rosie
    uv sync
    uv run rosie start
    ```

    [uv](https://docs.astral.sh/uv/) installs the right Python and every dependency.
    [DEVELOPMENT.md](https://github.com/PyForce/rosie/blob/main/DEVELOPMENT.md) has the rest: tests, lint,
    docs, the Docker image.

The PyPI package is `pyforce-rosie` because the name `rosie` was taken; you still `import rosie` and run
`rosie`.

## Drive the robot

**With WebRosie** (the Docker image serves it at <http://localhost:8080>):

- **Single Point Mode**: click the map, the robot goes there. In the settings, choose how many seconds it
  takes, and whether it goes around walls and furniture (the planner).
- **Path Mode**: click several points, then send the robot along them.
- **User Mode**: drive by hand, like a racing game: W and S for throttle, A and D to steer while moving, Q
  and E to turn on the spot (left and right). On a phone, a joystick.

**From Python**, with the [client](client.md):

```python
from rosie.client import RosieClient

robot = RosieClient("http://localhost:8080")  # 5000 without Docker
robot.goto(1, 0.5, 4)  # to (1 m, 0.5 m), in 4 s
for position in robot.positions():
    if position.distance_to(1, 0.5) < 0.02:
        break
print(robot.odometry())
```

**From the command line**, the web API is plain HTTP and JSON:

```bash
curl -X POST localhost:8080/goto -d '{"target": [1, 0.5, 4]}'
curl localhost:8080/odometry
```

## Configure it

`config.ini` says which robot rosie drives and what runs next to it:

```ini
[general]
loglevel = INFO
# the robot (see Robots and hardware)
profile = simubot
# your own robot profiles and maps, looked at before rosie's own
# profiles = ~/rosie/profiles
# maps = ~/rosie/maps
# the map the planner starts with
map = Gustavo's House
# logfile = rosie.log

# the web API (WebRosie, the Python client)
[web]
active = True
# 127.0.0.1: this computer only
host = 0.0.0.0
port = 5000

# a CSV file per planned movement
[recording]
directory = recordings
```

Each section other than `[general]` and `[recording]` is a plugin that runs when `active = True`: see
[Web API and plugins](integration.md).

With Docker, mount a folder with your `config.ini` (and `profiles/`, `maps/` if you have your own) on
`/config`:

```bash
docker run -p 8080:8080 -v ./my-rosie:/config ghcr.io/pyforce/rosie
```

## Simulate faster than real time

rosie takes its clock as a parameter, so a script can run the simulated robot as fast as Python goes, and
always get the same result. This is how rosie's own tests work, and the quickest way to experiment:

```python
from pathlib import Path

from rosie.planning.maps import DEFAULT_MAP, MAPS_DIR, list_maps
from rosie.profile import PROFILES_DIR, load_profile
from rosie.robot import Robot


class Clock:
    """Simulated time: it only moves when we say so."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


clock = Clock()
profile = load_profile("simubot", [PROFILES_DIR])
robot = Robot(profile, list_maps([MAPS_DIR]), DEFAULT_MAP, Path("recordings"), clock)

robot.follow([(1, 0), (1, 1), (0, 1)], 2)  # 2 s per side
for step in range(200):  # 10 s, computed in a blink
    clock.now += robot.sample_time
    robot.tick()

x, y, theta = robot.position()
print(f"x={x:.3f} m, y={y:.3f} m, theta={theta:.2f} rad")
```

The movement is also in `recordings/`, one row per control step: see
[Motion control](motion-control.md#watch-it-recordings).
