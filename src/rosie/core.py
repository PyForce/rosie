import logging
from collections.abc import Callable, Iterator, Sequence
from typing import Any

from rosie.models import Profile
from rosie.motion.controller import MovementController
from rosie.motion.models import Pose, TrajectoryParameters
from rosie.motion.supervisors import SupervisorContainer
from rosie.planning.planner import Planner

logger = logging.getLogger(__name__)


class Robot:
    """The robot core: everything rosie's interfaces can ask of the robot."""

    def __init__(
        self,
        profile: Profile,
        motion: MovementController,
        planner: Planner,
        sensors: dict[str, Callable[[], object]],
        supervisors: SupervisorContainer,
    ) -> None:
        self.profile = profile
        self.motion = motion
        self.planner = planner
        # sensor name -> function reading it (extensions can add theirs)
        self.sensors = sensors
        self.supervisors = supervisors

    @property
    def sample_time(self) -> float:
        return self.motion.sample_time

    def tick(self) -> None:
        self.motion.tick()

    def stop(self) -> None:
        self.motion.movement_finish()

    def position(self) -> tuple[float, float, float]:
        pose = self.motion.odometry_localizer.pose
        return pose.x, pose.y, pose.theta

    def teleport(self, x: float, y: float, theta: float) -> None:
        self.motion.odometry_localizer.pose = Pose(x, y, theta)

    def go_to(self, x: float, y: float, t: float) -> None:
        """Drive to (x, y) in t seconds."""
        self._check_duration(t)
        self._track(
            TrajectoryParameters([Pose(*self.position()), Pose(x, y, 0.0)], t, self.sample_time)
        )

    def go_to_with_planner(self, x: float, y: float, t: float) -> None:
        """Drive to (x, y) around walls and furniture, t seconds per straight stretch."""
        self._check_duration(t)
        x0, y0, _ = self.position()
        clearance = 0.2 * max(self.profile.body.width, self.profile.body.length)
        _start, *corners = self.planner.route((x0, y0), (x, y), clearance)
        self.follow(corners, t)

    def follow(self, points: Sequence[Sequence[float]], t: float) -> None:
        """Drive through the points in order, t seconds from one to the next."""
        self._check_duration(t)
        poses = [Pose(*self.position()), *(Pose(p[0], p[1], 0.0) for p in points)]
        self._track(TrajectoryParameters(poses, t, self.sample_time))

    def start_open_loop_control(self) -> None:
        logger.debug("set mode: MANUAL")
        self.motion.movement_init(None)
        self.motion.movement_start()

    def add_movement(self, direction: list[float]) -> None:
        self.motion.direction = direction

    def stop_open_loop_control(self) -> None:
        logger.debug("set mode: AUTO")
        self.motion.movement_finish()

    def supervisor(self) -> SupervisorContainer:
        return self.supervisors

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

    def _track(self, trajectory: TrajectoryParameters) -> None:
        self.motion.movement_init(trajectory)
        self.motion.movement_start()
