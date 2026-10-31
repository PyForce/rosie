"""The motor boards rosie drives, one module each, picked by the profile's [board] type."""

from rosie.errors import SetupError
from rosie.hardware.drive import arduino, md25, virtual
from rosie.hardware.drive.models import Drive, DriveFactory
from rosie.models import Clock, Profile


def open_drive(profile: Profile, clock: Clock) -> Drive:
    if profile.board not in DRIVES:
        raise SetupError(f"unsupported board: {profile.board} (known: {', '.join(DRIVES)})")
    return DRIVES[profile.board](profile, clock)


DRIVES: dict[str, DriveFactory] = {
    "virtual": virtual.open_drive,
    "arduino": arduino.open_drive,
    "md25": md25.open_drive,
}
