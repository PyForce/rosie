# How rosie works

## The control loop

A mobile robot is controlled in steps. Every `sample_time` seconds (0.05 s for the simulated robot), rosie
runs one **control step**:

```text
 encoders ──► wheel speeds ──► odometry ──► where the robot is
                                                  │
 trajectory ──► where it should be now ──► tracker ──► wheel speeds wanted
                                                              │
                     motors ◄── speed control (PID) ◄─────────┘
```

1. Read how far each wheel turned since the last step (the encoders), and work out the wheel speeds.
2. **Odometry**: update the robot's position from those two numbers.
3. Take the next point of the planned **trajectory**: where the robot should be now, and how fast it should
   be going.
4. The **tracker** compares the two and decides how fast each wheel should turn.
5. **Speed control** makes the wheels turn at those speeds: on the motor board itself, or in rosie (a PID).
6. Tell the **supervisors** what happened: the web API sends the new position to its clients, the recorder
   writes a row.

Under manual control, steps 3 and 4 are replaced by the pressed keys. That's all of
`MovementController.closed_loop_movement_control` in `motion/controller.py`, about 60 lines.

## One process, one loop, no threads

`rosie start` runs one Python process with one [asyncio](https://docs.python.org/3/library/asyncio.html)
event loop:

- `runner.run(robot)` calls `robot.tick()` every `sample_time` seconds. A late step doesn't make the next
  ones rush to catch up.
- Every active **plugin** (the web API, sensors) is a task on the same loop: `async def run(robot, settings)`.
- A stop signal (Ctrl+C, `docker stop`) stops the control loop first, then the motors, then the plugins.

So the robot code never needs locks: when a web request asks for the position, no control step is half done.
The robot core itself (`robot.py` and below) has no asyncio and no threads at all; it's plain Python you can
drive from a test, a notebook or your own loop.

## The robot is built from parts

`Robot` (in `robot.py`) puts the parts together from a [profile](robots.md#profiles):

| Part | Interface | rosie's implementations |
|---|---|---|
| Trajectory planner | `TrajectoryPlanner` | linear, cubic (`interpolation` in the profile) |
| Odometry | `OdometryLocalizer` | second-order Runge-Kutta |
| Trajectory tracker | `TrajectoryTracker` | input-output linearization |
| Motors | `MotorHandler` + a driver | simulated, Arduino board, MD25 board (`board` in the profile) |
| Route planner | `Planner` | visibility graph + A* |
| Supervisors | `MovementSupervisor` | web API, CSV recorder |

Each interface is a small abstract class, so replacing a part means writing one class: see
[writing your own tracker](motion-control.md#write-your-own-tracker).

## Time is a parameter

`Robot` takes a `clock`: a function returning the time in seconds. `rosie start` gives it `time.monotonic`;
tests and experiments give it a clock they move by hand, so a 10-second movement is simulated in
milliseconds and comes out the same every run ([example](getting-started.md#simulate-faster-than-real-time)).
The simulated motor board uses the same clock to integrate the wheel speeds.

## Where things are

```text
src/rosie/
├── __main__.py        the `rosie` command
├── process.py         rosie start: the robot, its control loop and its plugins
├── runner.py          the control loop's timing
├── robot.py           Robot: the parts put together, and what interfaces can ask of it
├── config.py          config.ini
├── profile.py         robot profiles (TOML)
├── errors.py
├── motion/
│   ├── models.py      Pose, Velocity, RobotParameters, RobotState
│   ├── controller.py  the control step; manual driving; the go-to-point controller
│   ├── odometry.py
│   ├── trajectories.py
│   ├── tracking.py
│   ├── motors.py      motor handlers and the speed PID
│   ├── supervisors.py
│   ├── recording.py   the CSV recorder
│   └── drivers/       simulated, Arduino, MD25 boards; serial and I2C
├── planning/          maps, visibility graph, A*, route planner
├── apis/web/          the REST + WebSocket API (FastAPI)
├── sensors/usound.py  the ultrasound board plugin
├── client/            the Python client
├── profiles/          built-in robots
└── maps/              built-in maps
```
