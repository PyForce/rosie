# rosie

**Learn mobile robotics by reading the robot.**

rosie is a complete robot stack (localization, planning, control, drives) for two-wheeled robots, written as
short Python modules you can read, change and run on a simulated robot or a real one. It estimates where the
robot is from its wheel encoders, plans routes around walls and furniture and trajectories along them, tracks
them with feedback controllers, and lets you drive by hand.

That is what rosie is for: learning and teaching how a mobile robot works, from the control equations to the
web page that drives it.

## What's inside

| You want to learn about | rosie's code | Read |
|---|---|---|
| Wheel odometry | `localization/odometry.py` | [Motion control](motion-control.md#where-is-the-robot-odometry) |
| Trajectory generation (linear, cubic) | `planning/trajectory.py` | [Motion control](motion-control.md#where-should-it-be-trajectories) |
| Trajectory tracking (input-output linearization) | `control/tracking.py` | [Motion control](motion-control.md#getting-there-trajectory-tracking) |
| Reaching a point (polar go-to-point) | `control/regulation.py` | [Motion control](motion-control.md#arriving-the-go-to-point-controller) |
| Wheel speed control (PID) | `hardware/drive/pid.py` | [Motion control](motion-control.md#turning-the-wheels-speed-control) |
| Route planning (visibility graph, A*) | `planning/path/` | [Navigation](navigation.md) |
| Talking to hardware (serial, I2C) | `hardware/` | [Robots and hardware](robots.md) |
| Robot software architecture | `core.py`, `robot.py`, `service.py` | [How rosie works](how-rosie-works.md) |
| Web APIs, WebSockets, clients | `apis/web/`, `client/` | [Web API and extensions](integration.md), [Python client](client.md) |

## Try it

```bash
docker run -p 8080:8080 ghcr.io/pyforce/rosie
```

Open <http://localhost:8080>: [WebRosie](https://github.com/PyForce/WebRosie), rosie's web interface, with a
simulated robot in a house. Click the map to send it somewhere. More ways to run it, and a first Python
script: [Getting started](getting-started.md).

## Where to go next

- [How rosie works](how-rosie-works.md): the control loop, and where each idea lives in the code.
- [Teaching with rosie](teaching.md): lab ideas, from odometry to writing your own controller.
- [Reference](reference.md): every module, class and function, straight from the code.
