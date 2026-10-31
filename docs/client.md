# Python client

`rosie.client` talks to a robot running rosie's [web API](integration.md), from a script or a notebook, on
Python 3.12 or newer. It needs only `websockets`:

```bash
pip install pyforce-rosie
```

```python
from rosie.client import RosieClient

robot = RosieClient("http://localhost:5000")
print(robot.metadata().name, "at", robot.odometry())
```

## Orders

```python
robot.goto(1, 0.5, 0.3)  # straight to (1 m, 0.5 m) at 0.3 m/s
robot.goto_with_planner(7.7, 1.2, 0.5)  # around walls and furniture, at 0.5 m/s
robot.follow([(1, 0), (1, 1)], 0.5)  # through the points, at 0.5 m/s
robot.follow_with_planner([(7.7, 1.2), (1, 1)], 0.5)  # through them, around walls and furniture
robot.teleport(0, 0, 0)  # tell the robot where it is
```

Orders return at once; the robot moves on its own. They raise what the robot itself would:

- `rosie.errors.NoRouteError` when the planner finds no way there;
- `ValueError` for an impossible order (a speed of 0, or faster than the wheels can go);
- `rosie.errors.RequestError` for anything else rosie refuses (it has `status` and `detail`).

## Watching

`positions()` gives the robot's position every time it moves, until you stop iterating:

```python
robot.goto(1, 0.5, 0.3)
for position in robot.positions():
    print(f"{position.x:.2f} {position.y:.2f}")
    if position.distance_to(1, 0.5) < 0.02:
        break
```

`odometry()` reads the position once. `sensor("usound")` reads a sensor.

## Driving by hand

Inside a `drive()` block the robot is under manual control, like WebRosie's Manual Mode:

```python
import time

with robot.drive() as wheel:
    wheel.move(steering=0, throttle=1, spin=0)  # forward
    time.sleep(1)
    wheel.move(steering=0, throttle=0, spin=-1)  # turn left on the spot
    time.sleep(0.5)
# the robot stops, and planned movements work again
```

Each command is in $[-1, 1]$: the steering (+1 right, while moving), the throttle (+1 forward) and the spin
(+1 clockwise, on the spot).

## Maps

```python
robot.maps()  # ["Gustavo's House", ...]
robot.current_map()  # the map the planner uses
robot.map("Garage")  # another one
robot.use_map("Garage")  # plan on it from now on
```

## Trajectory planners

```python
robot.trajectory_planners()  # (["linear", "cubic"], "linear"): the ones it knows, the one it uses
robot.use_trajectory_planner("cubic")  # for the next movements
```

A map is a GeoJSON `FeatureCollection`, as a dict: see [Maps](navigation.md#maps).

## History

The client started in 2017 as a separate repository,
[rosie-clientAPI](https://github.com/PyForce/rosie-clientAPI), by Sergio Frayle Pérez; it joined rosie, with
its history, for rosie 2.
