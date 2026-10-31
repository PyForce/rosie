"""The motor boards rosie drives, one module each, picked by the profile's [board] type."""

from rosie.boards import arduino, md25, virtual
from rosie.boards.models import Board, BoardFactory
from rosie.errors import SetupError
from rosie.models import Profile
from rosie.motion.models import Clock


def open_board(profile: Profile, clock: Clock) -> Board:
    if profile.board not in BOARDS:
        raise SetupError(f"unsupported board: {profile.board} (known: {', '.join(BOARDS)})")
    return BOARDS[profile.board](profile, clock)


BOARDS: dict[str, BoardFactory] = {
    "virtual": virtual.open_board,
    "arduino": arduino.open_board,
    "md25": md25.open_board,
}
