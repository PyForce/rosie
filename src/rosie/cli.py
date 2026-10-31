import asyncio
import logging
from pathlib import Path
from typing import Annotated, Final, Literal

import typer

from rosie import service
from rosie.errors import HardwareUnavailableError, SetupError
from rosie.models import Settings
from rosie.planning.maps import DEFAULT_MAP

LOG_FORMAT = "[%(asctime)-15s] %(levelname)s %(message)s"

# rosie's default configuration (DEFAULT_MAP comes with the maps)
DEFAULT_ROBOT_PROFILE: Final = "simubot"
DEFAULT_INTERFACES: Final = "web"
DEFAULT_HOST: Final = "0.0.0.0"  # noqa: S104 (a robot is driven from other machines)
DEFAULT_PORT: Final = 5000
DEFAULT_RECORD: Final = None
DEFAULT_LOG_LEVEL: Final = "INFO"

# The options of rosie start. A flag beats its environment variable, which beats the default.
RobotProfileOption = Annotated[
    str,
    typer.Option(
        "--robot-profile",
        envvar="ROSIE_ROBOT_PROFILE",
        help="One of rosie's robot profiles by name, or the folder of yours.",
    ),
]
MapOption = Annotated[
    str, typer.Option("--map", envvar="ROSIE_MAP", help="The map the planner starts with.")
]
InterfacesOption = Annotated[
    str,
    typer.Option(
        "--interfaces",
        envvar="ROSIE_INTERFACES",
        help='What gives the robot its orders, comma-separated; "" for the robot alone.',
    ),
]
HostOption = Annotated[
    str,
    typer.Option(
        "--host",
        envvar="ROSIE_HOST",
        help="Where the web API listens; 127.0.0.1: this computer only.",
    ),
]
PortOption = Annotated[int, typer.Option("--port", envvar="ROSIE_PORT", help="The web API's port.")]
RecordOption = Annotated[
    Path | None,
    typer.Option(
        "--record", envvar="ROSIE_RECORD", help="A folder for a CSV per planned movement."
    ),
]
LogLevelOption = Annotated[
    Literal["DEBUG", "INFO", "WARNING", "ERROR"],
    typer.Option("--log-level", envvar="ROSIE_LOG_LEVEL", case_sensitive=False),
]

app = typer.Typer(help="Modular robot control system", no_args_is_help=True)


@app.callback()
def rosie() -> None:
    # a callback keeps `start` a subcommand while it is the only one
    ...


@app.command()
def start(
    robot_profile: RobotProfileOption = DEFAULT_ROBOT_PROFILE,
    map_name: MapOption = DEFAULT_MAP,
    interfaces: InterfacesOption = DEFAULT_INTERFACES,
    host: HostOption = DEFAULT_HOST,
    port: PortOption = DEFAULT_PORT,
    record: RecordOption = DEFAULT_RECORD,
    log_level: LogLevelOption = DEFAULT_LOG_LEVEL,
) -> None:
    """Start the robot and its interfaces."""
    logging.basicConfig(format=LOG_FORMAT, level=log_level)
    settings = Settings(
        profile=robot_profile,
        map=map_name,
        interfaces=tuple(name.strip() for name in interfaces.split(",") if name.strip()),
        host=host,
        port=port,
        record=record.expanduser() if record else None,
    )
    try:
        asyncio.run(service.run(settings))
    except (SetupError, HardwareUnavailableError) as error:
        typer.echo(f"rosie: {error}", err=True)
        raise typer.Exit(1) from error
