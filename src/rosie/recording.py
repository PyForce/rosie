"""
Records every control step of a planned movement (goto, follow) into a CSV
file, to analyse how well the robot tracked it.

One file per movement, named after the time it ended (EYYYYmmddHHMMSS.csv).
The robot's wheels and control settings come first, as `# name = value` comment lines
(pandas: `read_csv(path, comment='#')`; MATLAB: `readtable(path,
'CommentStyle', '#')`).
"""

import csv
import io
import logging
import time
from dataclasses import asdict, astuple
from pathlib import Path

from rosie.control.models import RobotState
from rosie.models import STILL, Control, PIDGains, Row, Wheels

logger = logging.getLogger(__name__)

# time: s since the start; elapsed: s since the previous step; location in m, m, rad;
# tracker: speeds asked by the trajectory tracker; wheels in rad/s and A
COLUMNS = (
    "time", "elapsed",
    "x", "y", "theta",
    "ref_x", "ref_y", "ref_theta",
    "ref_speed_x", "ref_speed_y", "ref_speed_theta",
    "tracker_x", "tracker_y",
    "wheel_1_speed", "wheel_1_setpoint", "wheel_1_current",
    "wheel_2_speed", "wheel_2_setpoint", "wheel_2_current",
)  # fmt: skip


class MovementRecorder:
    """A MovementSupervisor that writes a CSV file per planned movement."""

    def __init__(
        self, wheels: Wheels, control: Control, gains: PIDGains | None, directory: Path
    ) -> None:
        # as the profile names them: wheels.radius, control.tracking.b...
        tables: dict[str, object] = {"wheels": asdict(wheels), "control": asdict(control)}
        if gains:
            tables["drive"] = {"gains": asdict(gains)}
        self.settings = _flatten("", tables)
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        self.rows: list[Row] | None = None  # None: not recording (manual control)
        self.time = 0.0

    def movement_begin(self, expected_updates: int | None) -> None:
        self.rows = None if expected_updates is None else []
        self.time = 0.0

    def movement_update(self, robot_state: RobotState) -> None:
        if self.rows is None:
            return
        self.time += robot_state.elapsed_time
        reference = robot_state.reference_pose or robot_state.pose
        velocity = robot_state.reference_velocity or STILL
        self.rows.append(
            (
                self.time,
                robot_state.elapsed_time,
                *astuple(robot_state.pose),
                *astuple(reference),
                *astuple(velocity),
                robot_state.tracker_x,
                robot_state.tracker_y,
                robot_state.wheel_1_speed,
                robot_state.wheel_1_setpoint,
                robot_state.wheel_1_current,
                robot_state.wheel_2_speed,
                robot_state.wheel_2_setpoint,
                robot_state.wheel_2_current,
            )
        )

    def movement_end(self) -> None:
        if not self.rows:
            return
        path = self.directory / f"{time.strftime('E%Y%m%d%H%M%S')}.csv"
        text = io.StringIO()
        for name, value in self.settings.items():
            text.write(f"# {name} = {value!r}\n")
        writer = csv.writer(text, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(self.rows)
        path.write_text(text.getvalue())
        logger.info("movement recorded in %s (%d steps)", path, len(self.rows))
        self.rows = None


def _flatten(prefix: str, table: dict[str, object]) -> dict[str, object]:
    flat: dict[str, object] = {}
    for key, value in table.items():
        if isinstance(value, dict):
            flat |= _flatten(f"{prefix}{key}.", value)
        else:
            flat[f"{prefix}{key}"] = value
    return flat
