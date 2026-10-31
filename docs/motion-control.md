# Motion control

This page follows one planned movement through rosie, from "go to (1, 0.5) in 4 s" to the motors, with the
equations and the code that implements each of them.

## The robot: a differential drive

Two wheels of radius $r$ on one axis, $L$ apart, each with its own motor; a caster keeps the robot level.
Its pose is $(x, y, \theta)$: the middle of the wheel axis, and its heading, counter-clockwise from the
$x$ axis. Wheel 1 is the left one, wheel 2 the right one.

If the wheels turn at $\omega_1$ and $\omega_2$ (rad/s), the robot moves forward at $v$ and turns at
$\omega$:

$$
v = r\,\frac{\omega_2 + \omega_1}{2} \qquad \omega = r\,\frac{\omega_2 - \omega_1}{L}
$$

and the other way round, the wheel speeds for a $v$ and $\omega$ we want:

$$
\omega_1 = \frac{v}{r} - \frac{\omega L}{2r} \qquad \omega_2 = \frac{v}{r} + \frac{\omega L}{2r}
$$

In rosie: `hardware/drive/kinematics.py` · `compute_wheel_speeds`, which every controller ends with.

The robot can't move sideways: it's *nonholonomic*, which is what makes controlling it interesting.

## Where is the robot? Odometry

`localization/odometry.py` · `advance`

Each step, the encoders say how many steps each wheel turned ($n$ steps per turn). As angles:
$\Delta\varphi_i = 2\pi\,\Delta\text{steps}_i / n$. The robot advanced and turned

$$
\Delta s = r\,\frac{\Delta\varphi_2 + \Delta\varphi_1}{2} \qquad \Delta\theta = r\,\frac{\Delta\varphi_2 - \Delta\varphi_1}{L}
$$

and the pose is updated using the heading halfway through the step (second-order Runge-Kutta), which is more
accurate on curves than using the heading at its start:

$$
x \mathrel{+}= \Delta s \cos\!\left(\theta + \tfrac{\Delta\theta}{2}\right) \quad
y \mathrel{+}= \Delta s \sin\!\left(\theta + \tfrac{\Delta\theta}{2}\right) \quad
\theta \mathrel{+}= \Delta\theta
$$

Odometry only adds up small movements, so its errors add up too: on a real robot, wheel slip and a slightly
wrong radius make the estimate drift. `POST /position` (`teleport`) tells rosie where the robot really is.

## Where should it be? Trajectories

`planning/trajectory.py`

A movement is a list of key points (the robot's position, then the targets) and a time per stretch. The
planner turns it into one reference per control step: a pose $(x_d, y_d, \theta_d)$ and a velocity
$(\dot x_d, \dot y_d, \dot\theta_d)$.

**Linear** (`plan_linear`): straight lines at constant speed, heading along the line. Simple,
but the heading jumps at every corner, which the robot can't do: watch it overshoot corners in a
[recording](#watch-it-recordings).

**Cubic** (`plan_cubic`): each stretch is a cubic polynomial in $s \in [0, 1]$:

$$
x(s) = s^3 x_f - (s-1)^3 x_i + \alpha_x s^2 (s-1) + \beta_x s (s-1)^2
$$

$$
\alpha_x = k\cos\theta_f - 3x_f \qquad \beta_x = k\cos\theta_i + 3x_i
$$

(and the same for $y$ with $\sin$). The curve starts at $(x_i, y_i)$ heading $\theta_i$ and ends at
$(x_f, y_f)$ heading $\theta_f$; $k$, here the length of the stretch, sets how strongly it leaves and
arrives along those headings. rosie picks the headings: the robot's own at the start, along the last stretch
at the end, and halfway between the incoming and outgoing directions at every point in between. The result
rounds the corners. The heading and turning speed come from the curve's derivatives:

$$
\theta_d = \operatorname{atan2}(\dot y, \dot x) \qquad \dot\theta_d = \frac{\ddot y \dot x - \ddot x \dot y}{\dot x^2 + \dot y^2}
$$

Pick one in the [profile](robots.md#profiles): `[planning] planner = "linear"` or `"cubic"`.

## Getting there: trajectory tracking

`control/tracking.py` · `track_by_io_linearization`

The tracker compares where the robot is with where it should be, every step, and asks for wheel speeds. A
differential drive can't be told "move to the left", so rosie doesn't control the middle of the axle but a
point $B$ at a distance $b$ in front of it:

$$
y_1 = x + b\cos\theta \qquad y_2 = y + b\sin\theta
$$

That point *can* move in any direction: its velocity relates to $(v, \omega)$ through an invertible matrix
(for $b \neq 0$). So we choose the velocity we want for $B$, the reference's velocity plus a correction
proportional to the error,

$$
u_1 = \dot y_{1d} + k_1 (y_{1d} - y_1) \qquad u_2 = \dot y_{2d} + k_2 (y_{2d} - y_2)
$$

and invert:

$$
v = u_1\cos\theta + u_2\sin\theta \qquad \omega = \frac{-u_1\sin\theta + u_2\cos\theta}{b}
$$

then turn $(v, \omega)$ into wheel speeds. The error of $B$ then shrinks exponentially, at rates $k_1$
and $k_2$. This is *input-output linearization*. In the profile, $b$ is `[control.tracking] lookahead`, and
$k_1$ and $k_2$ are `[control.tracking.gains]`: `k1`, `k2`.

## Arriving: the go-to-point controller

`control/regulation.py` · `go_to_point`

The tracker steers point $B$, not the robot's centre, and it can't hold a two-wheeled robot still on a
point. So when the trajectory is over, a second controller takes the robot the rest of the way. With $\rho$
the distance to the target and $\alpha$ its direction relative to the heading:

$$
v = K_\rho\,\rho\cos\alpha \qquad \omega = K_\alpha\,\alpha
$$

($K_\rho$ and $K_\alpha$ are `[control.regulation.gains]`: `distance` and `angle`, 1 and 3 by default). If
the target is behind, the robot backs up instead of turning around. The movement ends when the robot is within
`[control.regulation] tolerance` of the target, or `timeout` seconds after the planned time, with a warning in
the log.

## Turning the wheels: speed control

`hardware/drive/pid.py` · `regulate_speed`

Wheel speeds are what the tracker asks for; motors take power. Something has to close that loop:

- the **Arduino** drive runs its own speed controller; rosie sends it the gains at start-up;
- the **MD25** drive only takes powers, so rosie runs a PID for each wheel, in incremental form:

$$
u_k = u_{k-1} + k_c (e_k - e_{k-1}) + k_i\, e_k + k_d (e_k - 2e_{k-1} + e_{k-2})
$$

  limited to $\pm$`max_power` (the MD25's `[drive]`). Gains in the profile's `[drive.gains]`: `kc`, `ki`,
  `kd`.
- the **simulated** drive turns its wheels at exactly the speed asked, up to `max_speed`.

## Driving by hand

`control/teleoperation.py` · `steer`

Under manual control, the keyboard or the joystick (in WebRosie, or the Python client) gives three commands,
each in $[-1, 1]$: the steering, the throttle and the spin. Throttle turns both wheels at up to
`[control.teleoperation] max_speed` (8 rad/s by default);
steering slows the inner wheel, but only while moving, like a car; spin turns the wheels in opposite
directions, turning on the spot. No odometry is
needed to drive, but it keeps running, so the map still shows where the robot is.

## Watch it: recordings

`recording.py`

With `rosie start --record FOLDER` (or a folder passed to `Robot`), every planned movement is saved
as a CSV file: the robot's parameters as `#` comment lines, then one row per control step with the pose, the
reference, the tracker's output, and each wheel's speed, set point and current.

```python
from pathlib import Path

import pandas as pd

recording = sorted(Path("recordings").glob("*.csv"))[-1]
data = pd.read_csv(recording, comment="#")
error = ((data.x - data.ref_x) ** 2 + (data.y - data.ref_y) ** 2) ** 0.5
print(f"{len(data)} steps, largest tracking error {error.max():.3f} m")
```

Plot `x, y` against `ref_x, ref_y`, change a gain in the profile, and run it again.

## Write your own tracker

A tracker is a function: the reference pose and velocity, and the robot's pose, in; the two wheel speeds (and
two numbers of your choice for the recording) out. Its own settings come first, so `functools.partial` can
fix them. This one is the classic controller by Kanayama et al. (1990), which works with the errors in the
robot's own frame:

```python
import math

from rosie.control.models import TrackerOutput
from rosie.hardware.drive.kinematics import compute_wheel_speeds
from rosie.models import Pose, Velocity, Wheels


def kanayama(
    wheels: Wheels,
    kx: float,
    ky: float,
    ktheta: float,
    reference: Pose,
    reference_velocity: Velocity,
    pose: Pose,
) -> TrackerOutput:
    dx, dy = reference.x - pose.x, reference.y - pose.y
    ex = math.cos(pose.theta) * dx + math.sin(pose.theta) * dy
    ey = -math.sin(pose.theta) * dx + math.cos(pose.theta) * dy
    etheta = math.atan2(
        math.sin(reference.theta - pose.theta), math.cos(reference.theta - pose.theta)
    )
    v_ref = math.hypot(reference_velocity.x, reference_velocity.y)
    v = v_ref * math.cos(etheta) + kx * ex
    omega = reference_velocity.theta + v_ref * (ky * ey + ktheta * math.sin(etheta))
    return TrackerOutput(compute_wheel_speeds(v, omega, wheels), v, omega)
```

Give it to a robot, here the simulated one from
[Getting started](getting-started.md#simulate-faster-than-real-time):

```python
from functools import partial

robot.track = partial(kanayama, robot.profile.wheels, 2.0, 10.0, 4.0)
```

Then compare the two trackers' recordings on the same path.

## Further reading

- B. Siciliano, L. Sciavicco, L. Villani, G. Oriolo, *Robotics: Modelling, Planning and Control*, Springer,
  2009, chapter 11 (wheeled mobile robots): kinematics, odometry, cubic Cartesian trajectories,
  input-output linearization.
- Y. Kanayama, Y. Kimura, F. Miyazaki, T. Noguchi, "A stable tracking control method for an autonomous mobile
  robot", *IEEE ICRA*, 1990.
- P. Corke, *Robotics, Vision and Control*, Springer: "moving to a point", the go-to-point controller.
