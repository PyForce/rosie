import importlib
import sys


def main() -> None:
    try:
        # the command needs the `robot` extra; the client alone doesn't
        cli = importlib.import_module("rosie.cli")
    except ModuleNotFoundError as error:
        sys.exit(
            f"rosie needs the robot: pip install 'pyforce-rosie[robot]' (missing {error.name})"
        )
    cli.app()


if __name__ == "__main__":
    main()
