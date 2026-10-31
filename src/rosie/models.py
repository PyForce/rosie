from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class StartupOption:
    """Single setting of rosie start. A flag beats its environment variable, which beats the default."""

    name: str
    flag: str
    env: str
    default: str  # as it would come from the environment
    help: str
    type: Callable[[str], object]
    choices: tuple[str, ...] | None


@dataclass(frozen=True, slots=True)
class Settings:
    robot: str  # one of rosie's robots by name, or the folder of yours
    map: str  # the map the planner starts with
    host: str  # where the web API listens
    port: int
    record: Path | None  # folder for a CSV of every planned movement
