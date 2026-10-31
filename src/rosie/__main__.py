import argparse
import asyncio
import importlib
import logging
import os
from pathlib import Path

from rosie.const import OPTIONS
from rosie.models import Settings

LOG_FORMAT = "[%(asctime)-15s] %(levelname)s %(message)s"


def main() -> None:
    parser = argparse.ArgumentParser(prog="rosie", description="Modular robot control system")
    subparsers = parser.add_subparsers(title="subcommands", required=True)
    start = subparsers.add_parser(
        "start",
        help="start the robot and its web API",
        description="Start the robot and its web API. A flag beats its environment variable.",
    )
    for option in OPTIONS:
        start.add_argument(
            option.flag,
            dest=option.name,
            type=option.type,
            choices=option.choices,
            default=os.environ.get(option.env, option.default),
            help=f"{option.help} ({option.env}, default {option.default!r})",
        )
    args = parser.parse_args()

    try:
        # the robot needs the `robot` extra; the client alone doesn't
        service = importlib.import_module("rosie.service")
    except ModuleNotFoundError as error:
        msg = "rosie start needs the robot: pip install 'pyforce-rosie[robot]'"
        f"(missing {error.name})\n"
        parser.exit(1, msg)

    logging.basicConfig(format=LOG_FORMAT, level=args.log_level)
    settings = Settings(
        robot=args.robot,
        map=args.map,
        interfaces=tuple(name.strip() for name in args.interfaces.split(",") if name.strip()),
        host=args.host,
        port=args.port,
        record=Path(args.record).expanduser() if args.record else None,
    )
    asyncio.run(service.run(settings))


if __name__ == "__main__":
    main()
