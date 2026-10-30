from abc import ABC, abstractmethod

from rosie.motion.models import RobotState


class MovementSupervisor(ABC):
    """Follows each movement: its start, every control step, its end."""

    @abstractmethod
    def movement_begin(self, expected_updates: int | None) -> None:
        """`expected_updates`: control steps of a planned movement, None under manual control."""

    @abstractmethod
    def movement_update(self, robot_state: RobotState) -> None: ...

    @abstractmethod
    def movement_end(self) -> None: ...


class SupervisorContainer(MovementSupervisor, list[MovementSupervisor]):
    def movement_begin(self, expected_updates: int | None) -> None:
        for supervisor in self:
            supervisor.movement_begin(expected_updates)

    def movement_update(self, robot_state: RobotState) -> None:
        for supervisor in self:
            supervisor.movement_update(robot_state)

    def movement_end(self) -> None:
        for supervisor in self:
            supervisor.movement_end()
