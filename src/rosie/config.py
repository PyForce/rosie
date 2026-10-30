"""
rosie's configuration: an INI file with a [general] section and one section
per plugin to run (`active = True`).
"""

import configparser
from pathlib import Path

# written on the first start, when there is no configuration yet
DEFAULT_CONFIG = """\
[general]
loglevel = INFO
profile = simubot

[web]
active = True
"""


def load_config(path: Path) -> configparser.ConfigParser:
    if not path.exists():
        path.write_text(DEFAULT_CONFIG)
    config = configparser.ConfigParser(interpolation=None)
    config.read_string(path.read_text(), source=str(path))
    return config
