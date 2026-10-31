import logging
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import Any

from rosie.control.models import (
    ManualMovement,
    Movement,
    MovementObserver,
    PlannedMovement,
    Tracker,
)
from rosie.control.movement import MIN_MANUAL_ELAPSED_TIME, is_over, manual_step, planned_step
from rosie.errors import SetupError
from rosie.hardware.drive.models import Drive
from rosie.localization.odometry import advance, measure_speeds
from rosie.models import ORIGIN, Clock, Pose, Profile
from rosie.planning.models import TrajectoryPlanner, TrajectoryRequest, VisibilityGraph
from rosie.planning.path import plan_path
from rosie.planning.trajectory import plan
from rosie.planning.visibility import visibility_graph
from rosie.world.maps import load_world, read_map
from rosie.world.models import World

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
        trajectory_planner: TrajectoryPlanner,
        track: Tracker,
        map_files: dict[str, Path],
        world: World,
        sensors: dict[str, Callable[[], object]],
        observers: list[MovementObserver],
        clock: Clock,
    ) -> None:
        self.profile = profile
        self.drive = drive
        self.trajectory_planner = trajectory_planner
        self.track = track
        # map name -> its file; the world the robot moves in, and its visibility graph once a
        # route needs it
        self.map_files = map_files
        self.world = world
        self.graph: VisibilityGraph | None = None
        # sensor name -> function reading it (extensions can add theirs)
        self.sensors = sensors
        self.observers = observers
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
        control = self.profile.control
        match movement:
            case PlannedMovement() if is_over(movement, self.pose, now, control.regulation):
                self.stop()
                return
            case ManualMovement():
                elapsed_time = max(elapsed_time, MIN_MANUAL_ELAPSED_TIME)

        reading = self.drive.read()
        if not reading:
            logger.error("no reading from the drive")
            return
        wheels = self.profile.wheels
        speeds = measure_speeds(wheels, reading.steps_1, reading.steps_2, elapsed_time)
        self.pose = advance(self.pose, wheels, reading.steps_1, reading.steps_2)

        match movement:
            case PlannedMovement():
                self.movement, wheel_speeds, telemetry = planned_step(
                    movement,
                    self.pose,
                    speeds,
                    reading,
                    elapsed_time,
                    now,
                    wheels,
                    control.regulation,
                    self.track,
                )
            case ManualMovement():
                wheel_speeds, telemetry = manual_step(
                    movement,
                    self.pose,
                    speeds,
                    reading,
                    elapsed_time,
                    wheels,
                    control.teleoperation,
                )
        self.drive.set_speeds(*wheel_speeds, *speeds)
        for observer in self.observers:
            observer.movement_update(telemetry)

    def stop(self) -> None:
        self.movement = None
        self.drive.stop()
        for observer in self.observers:
            observer.movement_end()

    def position(self) -> tuple[float, float, float]:
        return self.pose.x, self.pose.y, self.pose.theta

    def teleport(self, x: float, y: float, theta: float) -> None:
        self.pose = Pose(x, y, theta)

    def goto(self, x: float, y: float, speed: float) -> None:
        """Drive straight to (x, y), at speed (m/s)."""
        self._check_speed(speed)
        self._start_planned([Pose(*self.position()), Pose(x, y, 0.0)], speed)

    def goto_with_planner(self, x: float, y: float, speed: float) -> None:
        """Drive to (x, y) around walls and furniture, at speed (m/s)."""
        self._check_speed(speed)
        x0, y0, _ = self.position()
        body = self.profile.body
        clearance = self.profile.planning.clearance * max(body.width, body.length)
        if self.graph is None:
            self.graph = visibility_graph(self.world, clearance)
        _start, *corners = plan_path(self.graph, (x0, y0), (x, y))
        self.follow(corners, speed)

    def follow(self, points: Sequence[Sequence[float]], speed: float) -> None:
        """Drive through the points in order, at speed (m/s)."""
        self._check_speed(speed)
        key_poses = [Pose(*self.position()), *(Pose(p[0], p[1], 0.0) for p in points)]
        self._start_planned(key_poses, speed)

    def start_manual(self) -> None:
        """Drive by hand, standing still until the first commands arrive."""
        logger.debug("manual control")
        for observer in self.observers:
            observer.movement_begin(None)
        self._start(ManualMovement(steering=0.0, throttle=0.0, spin=0.0))

    def move(self, steering: float, throttle: float, spin: float) -> None:
        """Under manual control, drive with these commands (see ManualMovement)."""
        if isinstance(self.movement, ManualMovement):
            self.movement = ManualMovement(steering, throttle, spin)

    def stop_manual(self) -> None:
        logger.debug("planned movements")
        self.stop()

    def maps(self) -> Iterator[str]:
        return iter(self.map_files)

    def get_map(self, map_name: str) -> dict[str, Any] | None:
        return read_map(self.map_files[map_name]) if map_name in self.map_files else None

    @property
    def map_name(self) -> str:
        return self.world.name

    def use_map(self, map_name: str) -> None:
        """Plan routes on this map from now on (SetupError if there's no such map)."""
        if map_name not in self.map_files:
            raise SetupError(f"unknown map: {map_name}")
        self.world = load_world(self.map_files[map_name])
        self.graph = None

    def _check_speed(self, speed: float) -> None:
        """Above 0, and no faster than the wheels can go."""
        wheels = self.profile.wheels
        top = wheels.max_speed * wheels.radius
        if not 0 < speed <= top:
            raise ValueError(f"the speed must be above 0 and at most {top:g} m/s")

    def _start_planned(self, key_poses: list[Pose], speed: float) -> None:
        request = TrajectoryRequest(key_poses, speed, self.sample_time)
        points = plan(self.trajectory_planner, request)
        for observer in self.observers:
            observer.movement_begin(len(points))
        self._start(PlannedMovement(tuple(points), 0, self.last_step))

    def _start(self, movement: Movement) -> None:
        self.drive.reset()
        self.last_step = self.clock()
        self.movement = movement
