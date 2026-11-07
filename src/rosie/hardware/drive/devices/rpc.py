import logging
from xmlrpc.client import ServerProxy

from rosie.hardware.drive.models import DriveReading, RpcDriveSettings
from rosie.models import Clock, Profile
from rosie.profile import read_table

logger = logging.getLogger(__name__)


class RpcDrive:
    def __init__(self, rpc_proxy: ServerProxy) -> None:
        self.proxy = rpc_proxy

    def read(self) -> DriveReading | None:
        values = self.proxy.read()
        return None if values is None else DriveReading(*values)

    def set_speeds(
        self, speed_1: float, speed_2: float, measured_1: float, measured_2: float
    ) -> None:
        self.proxy.set_speeds(speed_1, speed_2, measured_1, measured_2)

    def stop(self) -> None:
        self.proxy.stop()

    def reset(self) -> None:
        self.proxy.reset()


def open_drive(profile: Profile, _clock: Clock) -> RpcDrive:
    settings = read_table(
        RpcDriveSettings, profile.drive_settings, f"[drive] of {profile.folder_name}"
    )
    proxy = ServerProxy(settings.url, allow_none=True)
    return RpcDrive(proxy)
