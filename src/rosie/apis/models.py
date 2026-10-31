from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING

from rosie.models import Settings

if TYPE_CHECKING:
    from rosie.core import Robot

# an interface serves the robot while inside its context
type Interface = Callable[[Robot, Settings], AbstractAsyncContextManager[None]]
