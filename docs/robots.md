# Robots and hardware

## Profiles

A robot is a folder with a `profile.toml`, a `thumbnail.png` (its picture), a `vector.svg` (its icon on the
map) and, if you like, its own floor maps in `maps/` ([Navigation](navigation.md#maps)). rosie's own are in
`src/rosie/builtin/profiles/` and you pick them by name (`rosie start --robot-profile kevin`); yours by the path of
the folder (`rosie start --robot-profile ./my-robot`). To change a built-in robot, copy its folder.

```toml
name = "SIMUBOT"
trajectory = "linear"  # linear or cubic
# video = ":8085/stream.mjpeg"  # a camera stream served by another program, ":port/path" on this host

[body]  # m
length = 0.2  # front to back
width = 0.42
height = 0

[wheels]
radius = 0.05  # m
distance = 0.2995  # m between the wheels
encoder_steps = 360  # per wheel turn
max_speed = 20.0  # rad/s

[board]
type = "virtual"  # simulated

[control]
sample_time = 0.05  # s between control steps
arrival_tolerance = 0.01  # m: a planned movement ends this close to its last point
arrival_timeout = 5.0  # s it may take, after the planned time, to get that close

[control.tracking]  # input-output linearization
b = 0.1  # m, the tracked point ahead of the wheel axis
k1 = 1.0
k2 = 1.0

[control.speed]  # wheel speed PID (not used by the virtual board)
kc = 2.0
ki = 1.0
kd = 1.0
```

What each setting does: [Motion control](motion-control.md). The body's size also sets the planner's
[clearance](navigation.md#free-space). `[board]` says which motor board drives the wheels, and its settings:
see [Boards](#boards). A sensor the robot has is a `[sensors.<name>]` table, such as the
[ultrasound board](integration.md#the-ultrasound-board).

A profile from rosie 1 (with `board = "..."` and `interpolation = "..."` at the top) needs the `[board]`
table, `trajectory` instead of `interpolation`, and `max_power` moved from `[control.speed]` to an MD25's
`[board]`; rosie says so when it reads one.

## Built-in robots

| Profile | Name | Board | Notes |
|---|---|---|---|
| `simubot` | SIMUBOT | simulated | the default; no hardware needed |
| `kevin` | Kevin | Arduino | |
| `ltl` | LTL3.0 | Arduino | with a camera stream |
| `rovert` | RoverT | MD25 | |
| `blubot` | Bluebot | MD25 | |

## Boards

`boards/`

- **virtual** (`virtual.py`): a simulated board. The wheels turn exactly at the speeds asked (up to
  `max_speed`), and the encoders count what they turned, integrated over rosie's clock.
- **arduino** (`arduino.py`): the [rosie motor driver](https://github.com/PyForce/rosie-motordriver) shield
  on an Arduino, on a serial port. It controls the wheel speeds itself, with the profile's
  `[control.speed]` gains; rosie sends set points and reads encoder counts and the battery level in small
  binary packets (`struct`).
- **md25** (`md25.py`): the MD25 motor controller, on I2C. It only takes motor powers, so rosie runs the
  [speed PID](motion-control.md#turning-the-wheels-speed-control). It also reports the battery voltage and
  the motor currents, and rosie filters out encoder glitches.

Their `[board]` settings, with the defaults (`boards/models.py`):

```toml
[board]
type = "arduino"
port = "/dev/ttyACM0"
baudrate = 9600
```

```toml
[board]
type = "md25"
bus = 1  # I2C bus number
address = 0x58
max_power = 127.0  # powers go from -max_power to max_power
```

The libraries for serial ports and I2C (pyserial, smbus2) come with `pip install "pyforce-rosie[robot]"`.
If a board isn't there, rosie stops with a message such as *nothing answers on /dev/ttyACM0*.

## A real robot with Docker

The same image runs on a Raspberry Pi (arm64) or a PC. Give it the board's device and your robot's folder:

```bash
docker run -p 8080:8080 --device /dev/ttyACM0 -v ./my-robot:/robot ghcr.io/pyforce/rosie --robot-profile /robot
```

For I2C boards (MD25, the ultrasound board), pass the bus and the host's `i2c` group:

```bash
docker run -p 8080:8080 --device /dev/i2c-1 --group-add $(getent group i2c | cut -d: -f3) \
    -v ./my-robot:/robot ghcr.io/pyforce/rosie --robot-profile /robot
```

## Your own board

A board is a module in `boards/` with a class that has the four methods of `Board` (`boards/models.py`):

- `read_encoders()`: the encoder steps of both wheels since the last reading, the battery voltage and the
  motor currents;
- `set_speeds(speed_1, speed_2, measured_1, measured_2)`: the wheel speeds to reach, and the ones just
  measured. A board that controls the speeds itself sends the first two; one that only takes powers turns
  them into powers with rosie's speed PID (`motion/pid.py`), as the MD25 does;
- `stop()` and `reset()` (before each new movement).

It talks to its hardware through what it's given (a serial port, an I2C bus), so it can be tested with a
fake. The module also has an `open_board(profile, clock)`, which reads the `[board]` settings (a dataclass in
`boards/models.py`) and opens the hardware; add it to `BOARDS` in `boards/__init__.py`, under the name your
profiles use as the `[board]`'s `type`. The Arduino and MD25 boards, and their tests in `tests/boards/`, are
the examples to follow.
