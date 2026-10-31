"""The sensors a robot can have, one module each, named by the profile's [sensors.<name>] tables."""

from collections.abc import Callable

from rosie.errors import SetupError
from rosie.models import Profile
from rosie.sensors import usound
from rosie.sensors.models import SensorFactory


def open_sensors(profile: Profile) -> dict[str, Callable[[], object]]:
    """Sensor name -> the function reading it, for every sensor the profile names."""
    unknown = [name for name in profile.sensors if name not in SENSORS]
    if unknown:
        raise SetupError(f"unsupported sensor: {', '.join(unknown)} (known: {', '.join(SENSORS)})")
    return {name: SENSORS[name](table) for name, table in profile.sensors.items()}


SENSORS: dict[str, SensorFactory] = {"usound": usound.open_sensor}
