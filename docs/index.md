# rosie

**Mobile robots, in Python you can read.**

rosie drives differential-drive robots: two motorised wheels, like most robots in a robotics course. It
estimates where the robot is from its wheel encoders, plans trajectories, tracks them with a feedback
controller, finds routes around walls and furniture, and lets you drive by hand. Each of those is a short,
plain Python module you can open, change and test against a simulated robot, then run on a real one.

That is what rosie is for: learning and teaching how a mobile robot works, from the control equations to the
web page that drives it.

## What's inside

| You want to learn about | rosie's code | Read |
|---|---|---|
| Wheel odometry | `motion/odometry.py` | [Motion control](motion-control.md#where-is-the-robot-odometry) |
| Trajectory generation (linear, cubic) | `motion/trajectories.py` | [Motion control](motion-control.md#where-should-it-be-trajectories) |
| Trajectory tracking (input-output linearization) | `motion/tracking.py` | [Motion control](motion-control.md#getting-there-trajectory-tracking) |
| Reaching a point (polar go-to-point) | `motion/control.py` | [Motion control](motion-control.md#arriving-the-go-to-point-controller) |
| Wheel speed control (PID) | `motion/pid.py` | [Motion control](motion-control.md#turning-the-wheels-speed-control) |
| Route planning (visibility graph, A*) | `planning/` | [Navigation](navigation.md) |
| Talking to hardware (serial, I2C) | `boards/`, `sensors/`, `buses.py` | [Robots and hardware](robots.md) |
| Robot software architecture | `core.py`, `robot.py`, `service.py`, `ticker.py` | [How rosie works](how-rosie-works.md) |
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
