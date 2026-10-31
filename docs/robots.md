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

[drive]
type = "virtual"  # simulated

[control]
sample_time = 0.05  # s between control steps
arrival_tolerance = 0.01  # m: a planned movement ends this close to its last point
arrival_timeout = 5.0  # s it may take, after the planned time, to get that close

[control.tracking]  # input-output linearization
b = 0.1  # m, the tracked point ahead of the wheel axis
k1 = 1.0
k2 = 1.0
```

What each setting does: [Motion control](motion-control.md). The body's size also sets the planner's
[clearance](navigation.md#free-space). `[drive]` says what turns the wheels, with its settings and, for a
drive with a PID, its `[drive.gains]`: see [Drives](#drives). A sensor the robot has is a `[sensors.<name>]` table, such as the
[ultrasound board](integration.md#the-ultrasound-board).

A profile from rosie 1 (with `board = "..."` and `interpolation = "..."` at the top) needs a `[drive]` table
(`type = "..."` and the drive's settings), `trajectory` instead of `interpolation`, and its `[control.speed]`
gains as `[drive.gains]`, without `max_power` (an MD25's `[drive]` setting); rosie says so when it reads one.

## Built-in robots

| Profile | Name | Drive | Notes |
|---|---|---|---|
| `simubot` | SIMUBOT | simulated | the default; no hardware needed |
| `kevin` | Kevin | Arduino | |
| `ltl` | LTL3.0 | Arduino | with a camera stream |
| `rovert` | RoverT | MD25 | |
| `blubot` | Bluebot | MD25 | |

## Drives

`hardware/drive/`

A drive turns the two wheels at the speeds rosie asks, and reports what their encoders counted.

- **virtual** (`virtual.py`): a simulated drive. The wheels turn exactly at the speeds asked (up to
  `max_speed`), and the encoders count what they turned, integrated over rosie's clock.
- **arduino** (`arduino.py`): the [rosie motor driver](https://github.com/PyForce/rosie-motordriver) shield
  on an Arduino, on a serial port. It controls the wheel speeds itself, with the profile's
  `[drive.gains]`; rosie sends set points and reads encoder counts and the battery level in small
  binary packets (`struct`).
- **md25** (`md25.py`): the MD25 motor controller, on I2C. It only takes motor powers, so rosie runs the
  [speed PID](motion-control.md#turning-the-wheels-speed-control) with the profile's `[drive.gains]`. It also reports the battery voltage and
  the motor currents, and rosie filters out encoder glitches.

Their `[drive]` settings, with the defaults (`hardware/drive/models.py`), and the PID gains they need:

```toml
[drive]
type = "arduino"
port = "/dev/ttyACM0"
baudrate = 9600

[drive.gains]  # sent to the shield at start-up
kc = 3.75
ki = 1.25
kd = 1.25
```

```toml
[drive]
type = "md25"
bus = 1  # I2C bus number
address = 0x58
max_power = 127.0  # powers go from -max_power to max_power

[drive.gains]  # rosie's PID
kc = 3.75
ki = 1.25
kd = 1.25
```

The libraries for serial ports and I2C (pyserial, smbus2) come with `pip install "pyforce-rosie[robot]"`.
If a drive's hardware isn't there, rosie stops with a message such as *nothing answers on /dev/ttyACM0*.

## A real robot with Docker

The same image runs on a Raspberry Pi (arm64) or a PC. Give it the drive's device and your robot's folder:

```bash
docker run -p 8080:8080 --device /dev/ttyACM0 -v ./my-robot:/robot ghcr.io/pyforce/rosie --robot-profile /robot
```

For I2C boards (MD25, the ultrasound board), pass the bus and the host's `i2c` group:

```bash
docker run -p 8080:8080 --device /dev/i2c-1 --group-add $(getent group i2c | cut -d: -f3) \
    -v ./my-robot:/robot ghcr.io/pyforce/rosie --robot-profile /robot
```

## Your own drive

A drive is a module in `hardware/drive/` with a class that has the four methods of `Drive`
(`hardware/drive/models.py`):

- `read_encoders()`: the encoder steps of both wheels since the last reading, the battery voltage and the
  motor currents;
- `set_speeds(speed_1, speed_2, measured_1, measured_2)`: the wheel speeds to reach, and the ones just
  measured. A drive that controls the speeds itself sends the first two; one that only takes powers turns
  them into powers with rosie's speed PID (`hardware/drive/pid.py`), as the MD25 does;
- `stop()` and `reset()` (before each new movement).

It talks to its hardware through what it's given (a serial port, an I2C bus), so it can be tested with a
fake. The module also has an `open_drive(profile, clock)`, which reads the `[drive]` settings (a dataclass in
`hardware/drive/models.py`), and `profile.gains` if it runs a PID, and opens the hardware. Add it to `DRIVES`
in `hardware/drive/__init__.py`, under the name your profiles use as the `[drive]`'s `type`. The Arduino and
MD25 drives, and their tests in `tests/hardware/drive/`, are the examples to follow.
