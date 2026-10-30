<div align="center">

<img src="assets/logo.svg" alt="" width="96">

# rosie

**Modular robot control system**

[![QA](https://github.com/PyForce/rosie/actions/workflows/qa.yml/badge.svg)](https://github.com/PyForce/rosie/actions/workflows/qa.yml)
[![Release](https://img.shields.io/github/v/release/PyForce/rosie?label=release)](https://github.com/PyForce/rosie/releases/latest)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
<br>
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

<!-- Badges to move into the rows above once they apply:
[![PyPI](https://img.shields.io/pypi/v/pyforce-rosie)](https://pypi.org/project/pyforce-rosie/)
[![Docker image](https://img.shields.io/badge/docker-ghcr.io-2496ED?logo=docker&logoColor=white)](https://github.com/PyForce/rosie/pkgs/container/rosie)
[![Docs](https://readthedocs.org/projects/rosie/badge/?version=latest)](https://rosie.readthedocs.io)
-->

[Quick start](#quick-start) · [Usage](#usage) · [Development](#development)

</div>

---

rosie drives differential-drive mobile robots: it plans trajectories, tracks them, finds routes around walls and
furniture, and lets you drive by hand. It runs a simulated robot out of the box, and real ones with an Arduino or
MD25 motor board. Its web API is what [WebRosie](https://github.com/PyForce/WebRosie) talks to.

## Features

- **Robot profiles in TOML.** Wheels, body, boards and control gains, for built-in robots or your own.
- **Planned movements.** Go to a point or follow a path, with linear or cubic trajectories, until the robot gets there.
- **Route planning.** Around the walls and furniture of a map.
- **Manual driving.** Racing-game keys or a touch joystick through WebRosie.
- **Plugins.** A REST + WebSocket API and sensors, each switched on in the configuration.

## Quick start

```bash
docker run -p 8080:8080 ghcr.io/pyforce/rosie
```

Then open <http://localhost:8080>: WebRosie, with a simulated robot to drive. For a real robot, see
[DEVELOPMENT.md](DEVELOPMENT.md#building-a-docker-image).

From the source:

```bash
uv sync
uv run rosie start
```

The first start writes a `config.ini` (simulated robot, web API on port 5000).

## Usage

```bash
curl -X POST localhost:5000/goto -d '{"target": [1, 0.5, 4]}'   # to (1, 0.5) in 4 s
curl localhost:5000/odometry
```

The PyPI package is `pyforce-rosie` (the name `rosie` belongs to another project); it installs the `rosie` command
and the `rosie` Python package.

## Development

Setup, QA, docs and releases: [DEVELOPMENT.md](DEVELOPMENT.md).

## Contributing

Issues and pull requests are welcome; `make qa` must pass.

## License

MIT: see [LICENSE](LICENSE).

---

<sub>🚀 Project starter provided by [Cookie Pyrate v1.1.0](https://github.com/gvieralopez/cookie-pyrate/tree/v1.1.0)</sub>
