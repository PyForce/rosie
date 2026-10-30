import importlib
import logging
import os
from pathlib import Path

import numpy as np

from rosie.config import config as global_settings
from rosie.motion.controller import MovementController
from rosie.motion.models import Pose, RobotParameters, TrajectoryParameters
from rosie.motion.motors import (
    HardwareSpeedMotorHandler,
    PIDSpeedController,
    SoftwareSpeedMotorHandler,
)
from rosie.motion.odometry import RungeKutta2Localizer
from rosie.motion.recording import MovementRecorder
from rosie.motion.supervisors import SupervisorContainer
from rosie.motion.tracking import IOLinearizationTracker
from rosie.motion.trajectories import CubicTrajectoryPlanner, LinearTrajectoryPlanner
from rosie.planning.maps import list_maps
from rosie.planning.planner import Planner

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")

PLANNERS = {"LINEAR": LinearTrajectoryPlanner, "CUBIC": CubicTrajectoryPlanner}
LOCALIZERS = {"ODOMETRY_RK2": RungeKutta2Localizer}

ARDUINO_PORT = "/dev/ttyACM0"
ARDUINO_BAUDRATE = 9600


class Robot:
    def __init__(self, clock):
        self.profile_name = global_settings.get("general", "profile")
        self.profile = load_profile(self.profile_name)
        self.parameters = robot_parameters(self.profile)
        self.motion = movement_controller(self.profile, self.parameters, clock)
        self.planner = Planner()
        self.planner.use_map("Gustavo's House")
        logging.info("profile: %s", self.profile_name)

        # [recording] directory = ...: one CSV file per planned movement
        recordings = global_settings.get("recording", "directory")
        if recordings:
            self.supervisor().append(MovementRecorder(self.parameters, Path(recordings)))

    @property
    def sample_time(self):
        """
        Seconds between two control steps
        """
        return self.motion.sample_time

    def tick(self):
        """
        Run one control step (called every `sample_time` seconds)
        """
        self.motion.tick()

    def stop(self):
        """
        Stop any movement and the motors
        """
        self.motion.movement_finish()

    def go_to(self, x, y, t):
        """
        Allows the robot to go from the current position
        to a given point in time t.

        Example:

        >>> r = Robot()
        >>> r.go_to(3, 4, 10) # Goes to (3,4) in 10s
        """

        trajectory = TrajectoryParameters(
            [Pose(*self.position()), Pose(x, y, 0.0)],
            t,
            self.motion.robot_parameters.sample_time,
            0.0,
        )

        self.track(trajectory)

    def go_to_with_planner(self, x, y, t):
        start = self.position()[:-1]
        end = np.array([x, y])
        points = self.planner.get_points(start=start, end=end, robot=self)

        def add_t(points, t):
            points = np.array(points)
            lens = np.hypot(points[:, 0], points[:, 1])
            tpm = t / np.add.reduce(lens)
            npoints = np.zeros(shape=(points.shape[0], 3))
            npoints[:, :-1] = points
            npoints[:, -1] = tpm * lens
            return npoints

        npoints = add_t(points, t)

        if not points:
            logging.warning("no available path. start=%r, end=%r", start, end)
        else:
            self.follow(points, t)

    def follow(self, points, t):
        """
        Allows the robot to follow a set of given points in time t * len(points).

        Example:

        >>> r = Robot()
        >>> trajectory = [(1,2), (6,1), (0,0)]
        >>> t = 10
        >>> r.follow(trajectory, t)
        """

        locations = [Pose(p[0], p[1], 0.0) for p in points]
        pos = self.position()
        locations.insert(0, Pose(pos[0], pos[1], 0))

        trajectory = TrajectoryParameters(
            locations, t, self.motion.robot_parameters.sample_time, 0.0
        )

        self.track(trajectory)

    def track(self, trajectory_parameters):
        self.motion.movement_init(trajectory_parameters)
        self.motion.movement_start()

    def start_open_loop_control(self):
        logging.debug("set mode: MANUAL")
        self.motion.movement_init(None)
        self.motion.movement_start()

    def add_movement(self, direction):
        self.motion.direction = direction

    def stop_open_loop_control(self):
        logging.debug("set mode: AUTO")
        self.motion.movement_finish()

    def position(self, x=None, y=None, theta=None):
        """
        Get or set the position of the robot

        :param x: X value of (X,Y)
        :type x: float
        :param y: Y value of (X,Y)
        :type y: float
        :param theta: orientation
        :type theta: float
        :return: current position (when ``x``, ``y`` and ``theta`` are None)
        :type: tuple

        >>> r = Robot()
        >>> r.position(2,3,0.5)
        >>> r.position()
        (2, 3, 0.5)
        """
        # ---- get position ----
        if x is y is theta is None:
            x = self.motion.odometry_localizer.global_location.x
            y = self.motion.odometry_localizer.global_location.y
            z = self.motion.odometry_localizer.global_location.theta
            return x, y, z

        # ---- set position ----
        self.motion.odometry_localizer.global_location = Pose(x, y, theta)

    def supervisor(self):
        return self.motion.movement_supervisor

    def change_supervisor(self, newsupervisor):
        self.motion.movement_supervisor = newsupervisor

    def change_trajectory_planner(self, newplanner):
        self.motion.trajectory_planner = newplanner

    def maps(self):
        """
        Get all names for the maps
        """
        return (tmap["name"] for _, tmap in list_maps())

    def get_map(self, map_name):
        return self.planner.get_map(map_name)

    def use_map(self, map_name):
        self.planner.use_map(map_name)


def movement_controller(profile, parameters, clock):
    if profile.KINEMATICS != "DIFFERENTIAL":
        raise ValueError(f"unsupported KINEMATICS: {profile.KINEMATICS}")
    return MovementController(
        SupervisorContainer(),
        _choose(PLANNERS, "INTERPOLATION", profile.INTERPOLATION)(),
        _choose(LOCALIZERS, "LOCALIZER", profile.LOCALIZER)(parameters),
        IOLinearizationTracker(parameters),
        _choose(MOTOR_HANDLERS, "FILENAME", profile.FILENAME)(profile, parameters, clock),
        parameters,
        clock,
    )


def robot_parameters(profile):
    return RobotParameters(
        profile.RADIUS,
        profile.DISTANCE,
        profile.ENCODER_STEPS,
        profile.CONST_B,
        profile.CONST_K1,
        profile.CONST_K2,
        profile.CONST_KI,
        profile.CONST_KD,
        profile.CONST_KC,
        profile.MAX_POWER_BIN,
        -profile.MAX_POWER_BIN,
        profile.SAMPLE_TIME,
        profile.MAX_SPEED,
    )


def load_profile(name):
    if not os.path.isdir(os.path.join(PROFILES_DIR, name)):
        raise ValueError(f"unknown profile: {name}")
    return importlib.import_module(f"rosie.profiles.{name}.settings")


def _virtual_motors(profile, parameters, clock):
    from rosie.motion.drivers.virtual import VirtualMotorDriver

    return HardwareSpeedMotorHandler(
        VirtualMotorDriver(parameters.steps_per_revolution, parameters.max_speed, clock)
    )


def _arduino_motors(profile, parameters, _clock):
    from rosie.motion.drivers.arduino import ArduinoMotorDriver

    driver = ArduinoMotorDriver(profile.MAX_SPEED, ARDUINO_PORT, ARDUINO_BAUDRATE)
    driver.set_constants(parameters.constant_kc, parameters.constant_ki, parameters.constant_kd)
    return HardwareSpeedMotorHandler(driver)


def _md25_motors(profile, parameters, _clock):
    from rosie.motion.drivers.md25 import MD25MotorDriver

    speed_controller = PIDSpeedController(
        parameters.constant_kc,
        parameters.constant_ki,
        parameters.constant_kd,
        parameters.max_value_power,
        parameters.min_value_power,
    )
    return SoftwareSpeedMotorHandler(speed_controller, MD25MotorDriver(1, 0x58))


# the boards' driver files used to be chosen by name, profiles still say so
MOTOR_HANDLERS = {
    "VirtualMD.py": _virtual_motors,
    "ArduinoMD.py": _arduino_motors,
    "MD25.py": _md25_motors,
}


def _choose(options, setting, value):
    if value not in options:
        raise ValueError(f"unsupported {setting}: {value} (known: {', '.join(options)})")
    return options[value]
