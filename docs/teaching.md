# Teaching with rosie

rosie keeps each idea of mobile robotics in one short module, runs a simulated robot with no hardware, and
can simulate faster than real time from a plain Python script. That makes it a lab bench: students change one
piece, run the same movement, and compare. The same code then drives a real robot.

Each lab below says what students change and what they measure. They build on each other, but each one stands
alone.

## Setting up a class

- **No installation**: `docker run -p 8080:8080 ghcr.io/pyforce/rosie` on the teacher's computer, and
  every student drives a robot from the browser.
- **One robot each**: start several containers on different ports; WebRosie shows several robots on one map.
- **Python work**: `pip install "pyforce-rosie[robot]"`, or clone the repository and `uv sync`, and use the
  [fast simulation](getting-started.md#simulate-faster-than-real-time) in scripts or notebooks.

## Lab 1: odometry

*Read:* [Odometry](motion-control.md#where-is-the-robot-odometry), `localization/odometry.py`.

1. Drive a square by hand (Manual Mode) and come back to the start. Where does rosie think the robot is?
2. The simulated robot has no separate truth: its position *is* its odometry. Add one: a
   [observer](integration.md#extending-rosie) that integrates the wheel speeds of every `Telemetry`
   with a wheel radius 2 % off, and plot how the two positions drift apart along a path.
3. On a real robot: order a 1 m straight line, measure where it really stopped, and correct the profile's
   wheel `radius` (or `distance`, with a turn on the spot).
4. Replace the Runge-Kutta update with the simpler Euler one (the heading at the start of the step) and
   compare both on a tight circle.

## Lab 2: trajectories

*Read:* [Trajectories](motion-control.md#where-should-it-be-trajectories), `planning/trajectory.py`.

1. Follow the same square with `planner = "linear"` and `"cubic"`, with [recordings](motion-control.md#watch-it-recordings)
   on. Plot the reference paths and the driven ones.
2. Plot the reference speeds: where does the linear plan ask the impossible?
3. Change the cubic planner's $k$ (the tangent gain) and describe the shapes.

## Lab 3: trajectory tracking

*Read:* [Trajectory tracking](motion-control.md#getting-there-trajectory-tracking), `control/tracking.py`.

1. Change `k1`, `k2` (`[control.tracking.gains]`) and `lookahead` in the profile. Measure the largest and final tracking errors on the same path.
2. Push the robot off its path mid-movement (`teleport` it 10 cm aside) and watch how fast the error
   dies out, against the theory.
3. [Write your own tracker](motion-control.md#write-your-own-tracker) (the Kanayama controller, a
   pure-pursuit one, ...) and compare it with input-output linearization.

## Lab 4: speed control

*Read:* [Speed control](motion-control.md#turning-the-wheels-speed-control), `hardware/drive/pid.py`.

1. The PID is tested on its own in `tests/hardware/drive/test_pid.py`: extend it with a simple motor model
   (first-order lag) and plot step responses for different gains.
2. On a robot with an MD25 drive, record a movement and plot each wheel's speed against its set point.

## Lab 5: navigation

*Read:* [Navigation](navigation.md), `planning/path.py`, `world/maps.py`.

1. Draw a map of your lab room (GeoJSON, with [geojson.io](https://geojson.io)) and drive the robot across it
   with the planner.
2. Plot the visibility graph on top of the map, for two clearances.
3. Count the vertices A* explores with and without its heuristic.

## Lab 6: integration

*Read:* [Web API and extensions](integration.md), [Python client](client.md).

1. Write a client script that drives the robot through a list of waypoints and logs the arrival times.
2. Add a sensor (a simulated distance sensor that uses the map and the robot's pose)
   and read it at `/sensor/...`.
3. Write a observer that stops the robot when it gets too close to an obstacle.

## Testing students' code

rosie's own test suite (`tests/`, pytest) shows how to test robot code without a robot: a fake clock, fake
serial ports and I2C buses, and the web API through FastAPI's test client. The same tools work for grading:
run a student's tracker on a fixed path and check the final error.
