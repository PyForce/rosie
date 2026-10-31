import logging
from collections.abc import Callable, Iterator, Sequence
from typing import Any

from rosie.control.models import Manual, Movement, MovementSupervisor, Planned, Tracker
from rosie.control.movement import MIN_MANUAL_ELAPSED_TIME, is_over, manual_step, planned_step
from rosie.hardware.drive.models import Drive
from rosie.localization.odometry import advance, measured_speeds
from rosie.models import ORIGIN, Clock, Pose, Profile
from rosie.planning.models import TrajectoryParameters, TrajectoryShape
from rosie.planning.path.planner import Planner
from rosie.planning.trajectory import plan

logger = logging.getLogger(__name__)


class Robot:
    """
    The robot core: everything rosie's interfaces can ask of the robot, and its
    state. Each tick reads the drive, runs one control step (control/movement.py)
    and writes the drive.
    """

    def __init__(
        self,
        profile: Profile,
        drive: Drive,
        shape: TrajectoryShape,
        track: Tracker,
        planner: Planner,
        sensors: dict[str, Callable[[], object]],
        supervisors: list[MovementSupervisor],
        clock: Clock,
    ) -> None:
        self.profile = profile
        self.drive = drive
        self.shape = shape
        self.track = track
        self.planner = planner
        # sensor name -> function reading it (extensions can add theirs)
        self.sensors = sensors
        self.supervisors = supervisors
        self.clock = clock
        self.pose = ORIGIN
        self.movement: Movement | None = None
        self.last_step = clock()

    @property
    def sample_time(self) -> float:
        return self.profile.control.sample_time

    def tick(self) -> None:
        movement = self.movement
        if movement is None:
            return
        now = self.clock()
        elapsed_time = now - self.last_step
        self.last_step = now
        match movement:
            case Planned() if is_over(movement, self.pose, now, self.profile.control):
                self.stop()
                return
            case Manual():
                elapsed_time = max(elapsed_time, MIN_MANUAL_ELAPSED_TIME)

        reading = self.drive.read_encoders()
        if not reading:
            logger.error("no reading from the drive")
            return
        wheels = self.profile.wheels
        delta_steps_1, delta_steps_2, *_ = reading
        speeds = measured_speeds(wheels, delta_steps_1, delta_steps_2, elapsed_time)
        self.pose = advance(self.pose, wheels, delta_steps_1, delta_steps_2)

        match movement:
            case Planned():
                self.movement, set_points, state = planned_step(
                    movement, self.pose, speeds, reading, elapsed_time, now, wheels, self.track
                )
            case Manual():
                set_points, state = manual_step(
                    movement, self.pose, speeds, reading, elapsed_time, wheels
                )
        self.drive.set_speeds(*set_points, *speeds)
        for supervisor in self.supervisors:
            supervisor.movement_update(state)

    def stop(self) -> None:
        self.movement = None
        self.drive.stop()
        for supervisor in self.supervisors:
            supervisor.movement_end()

    def position(self) -> tuple[float, float, float]:
        return self.pose.x, self.pose.y, self.pose.theta

    def teleport(self, x: float, y: float, theta: float) -> None:
        self.pose = Pose(x, y, theta)

    def goto(self, x: float, y: float, t: float) -> None:
        """Drive to (x, y) in t seconds."""
        self._check_duration(t)
        self._start_planned([Pose(*self.position()), Pose(x, y, 0.0)], t)

    def goto_with_planner(self, x: float, y: float, t: float) -> None:
        """Drive to (x, y) around walls and furniture, t seconds per straight stretch."""
        self._check_duration(t)
        x0, y0, _ = self.position()
        clearance = 0.2 * max(self.profile.body.width, self.profile.body.length)
        _start, *corners = self.planner.route((x0, y0), (x, y), clearance)
        self.follow(corners, t)

    def follow(self, points: Sequence[Sequence[float]], t: float) -> None:
        """Drive through the points in order, t seconds from one to the next."""
        self._check_duration(t)
        self._start_planned([Pose(*self.position()), *(Pose(p[0], p[1], 0.0) for p in points)], t)

    def start_manual(self) -> None:
        """Drive by hand, standing still until the first keys arrive."""
        logger.debug("manual control")
        for supervisor in self.supervisors:
            supervisor.movement_begin(None)
        self._start(Manual((0.0, 0.0, 0.0)))

    def move(self, keys: Sequence[float]) -> None:
        """The pressed keys under manual control: x (steer), y (throttle), rotation."""
        if isinstance(self.movement, Manual):
            x, y, rotation = keys
            self.movement = Manual((x, y, rotation))

    def stop_manual(self) -> None:
        logger.debug("planned movements")
        self.stop()

    def maps(self) -> Iterator[str]:
        return iter(self.planner.maps)

    def get_map(self, map_name: str) -> dict[str, Any] | None:
        return self.planner.get_map(map_name)

    @property
    def map_name(self) -> str | None:
        return self.planner.map_name

    def use_map(self, map_name: str) -> None:
        """Plan routes on this map from now on (ValueError if there's no such map)."""
        self.planner.use_map(map_name)

    def _check_duration(self, t: float) -> None:
        if t < self.sample_time:
            raise ValueError(f"the time must be at least one control step ({self.sample_time} s)")

    def _start_planned(self, key_poses: list[Pose], t: float) -> None:
        references = plan(self.shape, TrajectoryParameters(key_poses, t, self.sample_time))
        for supervisor in self.supervisors:
            supervisor.movement_begin(len(references))
        self._start(Planned(tuple(references), 0, self.last_step))

    def _start(self, movement: Movement) -> None:
        self.drive.reset()
        self.last_step = self.clock()
        self.movement = movement
