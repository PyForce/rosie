"""
Records every control step of a planned movement (goto, follow) into a CSV
file, to analyse how well the robot tracked it.

One file per movement, named after the time it ended (EYYYYmmddHHMMSS.csv).
The robot's parameters come first, as `# name = value` comment lines
(pandas: `read_csv(path, comment='#')`; MATLAB: `readtable(path,
'CommentStyle', '#')`).
"""

import csv
import io
import logging
import time
from dataclasses import astuple
from pathlib import Path

from rosie.motion.models import STILL, RobotParameters, RobotState
from rosie.motion.supervisors import MovementSupervisor

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

PARAMETERS = (
    "wheel_radius", "wheel_distance",
    "constant_b", "constant_k1", "constant_k2",
    "constant_kc", "constant_ki", "constant_kd",
)  # fmt: skip

type Row = tuple[float | None, ...]


class MovementRecorder(MovementSupervisor):
    def __init__(self, robot_parameters: RobotParameters, directory: Path) -> None:
        self.robot_parameters = robot_parameters
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
        for name in PARAMETERS:
            text.write(f"# {name} = {getattr(self.robot_parameters, name)!r}\n")
        writer = csv.writer(text, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(self.rows)
        path.write_text(text.getvalue())
        logger.info("movement recorded in %s (%d steps)", path, len(self.rows))
        self.rows = None
