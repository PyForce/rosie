from rosie.models import StartupOption

ROBOT = StartupOption(
    name="robot",
    flag="--robot",
    env="ROSIE_ROBOT",
    default="simubot",
    help="one of rosie's robots by name, or the folder of yours",
    type=str,
    choices=None,
)
MAP = StartupOption(
    name="map",
    flag="--map",
    env="ROSIE_MAP",
    default="Gustavo's House",
    help="the map the planner starts with",
    type=str,
    choices=None,
)
HOST = StartupOption(
    name="host",
    flag="--host",
    env="ROSIE_HOST",
    default="0.0.0.0",  # noqa: S104 (a robot is driven from other machines)
    help="where the web API listens; 127.0.0.1 for this computer only",
    type=str,
    choices=None,
)
PORT = StartupOption(
    name="port",
    flag="--port",
    env="ROSIE_PORT",
    default="5000",
    help="the web API's port",
    type=int,
    choices=None,
)
RECORD = StartupOption(
    name="record",
    flag="--record",
    env="ROSIE_RECORD",
    default="",
    help="a folder for a CSV file per planned movement; empty: no recording",
    type=str,
    choices=None,
)
LOG_LEVEL = StartupOption(
    name="log_level",
    flag="--log-level",
    env="ROSIE_LOG_LEVEL",
    default="INFO",
    help="how much rosie logs",
    type=str.upper,
    choices=("DEBUG", "INFO", "WARNING", "ERROR"),
)
OPTIONS = (ROBOT, MAP, HOST, PORT, RECORD, LOG_LEVEL)
