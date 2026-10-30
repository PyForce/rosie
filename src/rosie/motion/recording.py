"""
Records every control step of a planned movement (goto, follow) into a CSV
file, to analyse how well the robot tracked it.

One file per movement, named after the time it ended (EYYYYmmddHHMMSS.csv).
The robot's parameters come first, as `# name = value` comment lines
(pandas: `read_csv(path, comment='#')`; MATLAB: `readtable(path,
'CommentStyle', '#')`).
"""

import csv
import logging
import os
import time

from rosie.motion.supervisors import DifferentialDriveMovementSupervisor

__author__ = "Silvio"

COLUMNS = (
    "time",
    "elapsed",  # s since the start, s since the previous step
    "x",
    "y",
    "theta",  # location (m, m, rad)
    "ref_x",
    "ref_y",
    "ref_theta",  # reference location
    "ref_speed_x",
    "ref_speed_y",
    "ref_speed_theta",  # reference speed
    "tracker_x",
    "tracker_y",  # speeds asked by the trajectory tracker
    "wheel_1_speed",
    "wheel_1_setpoint",
    "wheel_1_current",  # rad/s, rad/s, A
    "wheel_2_speed",
    "wheel_2_setpoint",
    "wheel_2_current",
)

PARAMETERS = (
    "wheel_radius",
    "wheel_distance",
    "constant_b",
    "constant_k1",
    "constant_k2",
    "constant_kc",
    "constant_ki",
    "constant_kd",
)


class MovementRecorder(DifferentialDriveMovementSupervisor):
    """
    Supervisor that writes each planned movement to a CSV file in `directory`
    """

    def __init__(self, robot_parameters, directory):
        super(MovementRecorder, self).__init__()
        self.robot_parameters = robot_parameters
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
        self.rows = None  # None: not recording (manual control)
        self.expected_updates = None
        self.time = 0.0

    def movement_begin(self, expected_updates):
        """
        @param expected_updates: number of control steps of the movement,
            None for manual control (not recorded)
        """
        self.expected_updates = expected_updates
        self.rows = None if expected_updates is None else []
        self.time = 0.0

    def movement_update(self, robot_state):
        if self.rows is None or len(self.rows) >= self.expected_updates:
            return
        self.time += robot_state.elapsed_time
        location = robot_state.location
        reference = robot_state.reference_location
        speed = robot_state.reference_speed
        self.rows.append(
            (
                self.time,
                robot_state.elapsed_time,
                location.x_position,
                location.y_position,
                location.z_position,
                reference.x_position,
                reference.y_position,
                reference.z_position,
                speed.x_speed,
                speed.y_speed,
                speed.z_speed,
                robot_state.x_speed_ref,
                robot_state.y_speed_ref,
                robot_state.angular_speed_1,
                robot_state.set_point_1,
                robot_state.current_1,
                robot_state.angular_speed_2,
                robot_state.set_point_2,
                robot_state.current_2,
            )
        )

    def movement_end(self):
        if not self.rows:
            return
        path = os.path.join(self.directory, time.strftime("E%Y%m%d%H%M%S") + ".csv")
        with open(path, "w", newline="") as csv_file:
            for name in PARAMETERS:
                csv_file.write("# %s = %r\n" % (name, getattr(self.robot_parameters, name)))
            writer = csv.writer(csv_file, lineterminator="\n")
            writer.writerow(COLUMNS)
            writer.writerows(self.rows)
        logging.info("movement recorded in %s (%d steps)", path, len(self.rows))
        self.rows = None
