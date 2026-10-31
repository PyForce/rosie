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
5. **Speed control** makes the wheels turn at those speeds: on the drive itself, or in rosie (a PID).
6. Tell the **supervisors** what happened: the web API sends the new position to its clients, the recorder
   writes a row.

Under manual control, steps 3 and 4 are replaced by the driving commands (steering, throttle, spin). `Robot.tick` (in `core.py`) does the
reading and the writing; the step itself is a function in `control/movement.py`, `planned_step` or
`manual_step`: the movement, the pose and the measured speeds in; the wheel speeds to ask for and the step's
`RobotState` out. The movement is a value too: `Planned` (the references, and the next one to follow) or
`Manual` (the steering, throttle and spin).

## One process, one loop, no threads

`rosie start` runs one Python process with one [asyncio](https://docs.python.org/3/library/asyncio.html)
event loop:

- The control loop (`run_every` in `service.py`) calls `robot.tick()` every `sample_time` seconds. A late step doesn't make
  the next ones rush to catch up.
- Each interface (the web API, by default) is a task on the same loop.
- A stop signal (Ctrl+C, `docker stop`) stops the control loop first, then the motors, then the interfaces.

That's all of `service.py`:

```python
async with start_interfaces(robot, settings, interfaces), start_control_loop(robot):
    await stop.wait()
```

A new interface is a function from the robot and the settings to an async context manager that serves it
while inside, added to `INTERFACES` in `service.py`.

So the robot code never needs locks: when a web request asks for the position, no control step is half done.
The robot core itself (`core.py` and below) has no asyncio and no threads at all; it's plain Python you can
drive from a test, a notebook or your own loop.

## The robot is built from parts

`build_robot` (in `robot.py`) puts a `Robot` together from the parts a [profile](robots.md#profiles) names:

| Part | Shape | rosie's |
|---|---|---|
| Trajectory | a function, `TrajectoryShape` | `plan_linear`, `plan_cubic` (`trajectory` in the profile) |
| Odometry | a function | `advance`: second-order Runge-Kutta |
| Trajectory tracker | a function, `Tracker` | `track_by_io_linearization`: input-output linearization |
| Drive | a class with the `Drive` methods | simulated, Arduino, MD25 (`[drive]` in the profile) |
| Route planner | `Planner` | visibility graph + A* |
| Supervisors | a class with the `MovementSupervisor` methods | web API, CSV recorder |

The math is plain functions on frozen dataclasses, one equation each, so replacing a part means writing one
function: see [writing your own tracker](motion-control.md#write-your-own-tracker). Classes are left where
there is real state: the drives (their hardware), the supervisors, and the robot itself.

## Time is a parameter

`build_robot` takes a `clock`: a function returning the time in seconds. `rosie start` gives it `time.monotonic`;
tests and experiments give it a clock they move by hand, so a 10-second movement is simulated in
milliseconds and comes out the same every run ([example](getting-started.md#simulate-faster-than-real-time)).
The simulated drive uses the same clock to integrate the wheel speeds.

## Where things are

```text
src/rosie/
├── __main__.py           the `rosie` command (it needs the `robot` extra)
├── cli.py                rosie start and its options (Typer)
├── service.py            rosie start: the robot, its control loop and its interfaces
├── core.py               Robot: its state, its tick, and what interfaces can ask of it
├── robot.py              build_robot: a Robot from its profile
├── profile.py            reading a profile.toml
├── models.py             Settings, Profile and its tables, Pose, the types every layer shares
├── recording.py          the CSV recorder
├── errors.py
├── hardware/             what the robot is made of
│   ├── drive/            the motors, their encoders, the wheel-speed loop
│   │   ├── devices/      virtual.py, arduino.py, md25.py: one module per drive
│   │   ├── kinematics.py the differential-drive model
│   │   ├── pid.py        speed control, for drives that only take powers (MD25)
│   │   └── models.py     Drive, its settings
│   ├── sensors/          the ultrasound board, and its settings (models.py)
│   ├── buses.py          opening serial ports and I2C buses
│   └── models.py         SerialPort, I2CBus
├── localization/         where the robot is
│   └── odometry.py       encoder steps → wheel speeds and pose
├── planning/             where it should be
│   ├── trajectory.py     key poses → one reference per control step (linear, cubic)
│   └── path/             around walls and furniture: maps, visibility graph, A*, the planner
├── control/              how to get there
│   ├── tracking.py       follow a trajectory (input-output linearization)
│   ├── regulation.py     stop on a point (the go-to-point controller)
│   ├── teleoperation.py  driving by hand: steering, throttle, spin
│   ├── movement.py       one control step: which controller, when a movement ends
│   └── models.py         Planned, Manual, RobotState, MovementSupervisor
├── apis/                 what an interface is (models.py: Interface)
│   └── web/              the REST + WebSocket API (FastAPI)
├── client/               the Python client
└── builtin/
    ├── profiles/         rosie's own robot profiles
    └── maps/             rosie's own maps
```
