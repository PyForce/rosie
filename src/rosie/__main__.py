r"""
      ___  ____
 _ _ / _ \/ ___\ _
| '_| | | \___ \(_)
| | | |_| |___) | |
|_|  \___/\____/|_|

"""

import argparse
import asyncio
import importlib
import logging
from pathlib import Path

from rosie.config import load_config

LOG_FORMAT = "[%(asctime)-15s] %(levelname)s %(message)s"


def main() -> None:
    parser = argparse.ArgumentParser(prog="rosie", description="Modular robot control system")
    parser.add_argument("--config", type=Path, default=Path("config.ini"), help="INI file to use")
    subparsers = parser.add_subparsers(title="subcommands", required=True)
    subparsers.add_parser("start", help="start the robot and its active plugins")
    args = parser.parse_args()

    try:
        # the robot needs the `robot` extra; the client alone doesn't
        process = importlib.import_module("rosie.process")
    except ModuleNotFoundError as error:
        parser.exit(
            1,
            f"rosie start needs the robot: pip install 'pyforce-rosie[robot]' (missing {error.name})\n",
        )

    config = load_config(args.config)
    logging.basicConfig(
        format=LOG_FORMAT,
        level=config.get("general", "loglevel", fallback="INFO").upper(),
        filename=config.get("general", "logfile", fallback=None),
    )
    asyncio.run(process.run(config))


if __name__ == "__main__":
    main()
