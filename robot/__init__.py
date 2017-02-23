import os
import logging

from settings import config as global_settings

from robot.motion.Localizer.Method.RungeKutta import RungeKutta2OdometryLocalizer
from robot.motion.MotorHandler.Differential import HardSpeedControlledMH
from robot.motion.MotorHandler.Differential import SoftSpeedControlledMH
from robot.motion.MovementController.Differential import DifferentialDriveRobotParameters, \
    DifferentialDriveMovementController, \
    DifferentialDriveRobotLocation
from robot.motion.MotorHandler.SpeedController.Controller.PID import PIDSpeedController
from robot.motion.TrajectoryPlanner.Differential import DifferentialDriveTrajectoryParameters
from robot.motion.TrajectoryPlanner.Planner.Cubic import CubicTrajectoryPlanner
from robot.motion.TrajectoryPlanner.Planner.Linear import LinearTrajectoryPlanner
from robot.motion.TrajectoryTracker.Tracker.IOLinearization import IOLinearizationTrajectoryTracker
from robot.motion.MovementTimer import DefaultTimer
from robot.motion.MovementSupervisor.Differential import SupervisorContainer


from tools.singleton import Singleton
from robot.planning.planner import Planner


class SettingHandler:

    def __init__(self):
        self.profile = global_settings.get('general', 'profile')
        if os.path.exists(os.path.join(os.getcwd(), 'profiles', self.profile)):
            try:
                import importlib
                self.settings = importlib.import_module(
                    "profiles.%s.settings" % self.profile)
                self.parameters = self.buildRobotParameters()
                logging.info('load profile: ' + self.profile)
            except ImportError:
                self.settings = None
                logging.error("problem loading <" + self.profile + ">")
        else:
            logging.error("directory <" + self.profile + "> do not exist")

    def buildMovementControllers(self):
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            supervisor = self.buildMovementSupervisor()
            planner = self.buildTrajectoryPlanner()
            localizer = self.buildLocalizer()
            tracker = self.buildTrajectoryTracker()
            motror_handler = self.buildMotorHandler()
            timer = self.buildTimer()

            return DifferentialDriveMovementController(supervisor,
                                                       planner,
                                                       localizer,
                                                       tracker,
                                                       motror_handler,
                                                       timer,
                                                       self.parameters)
        else:
            logging.error("kinematic model not supported")
            return None

    def buildLocalizer(self):
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            if self.settings.LOCALIZER == 'ODOMETRY_RK2':
                return RungeKutta2OdometryLocalizer(self.parameters)
            else:
                logging.error("localizer not supported")
                return None
        else:
            logging.error("kinematic model not supported")
            return None

    def buildTrajectoryPlanner(self):
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            if self.settings.INTERPOLATION == 'LINEAR':
                return LinearTrajectoryPlanner()
            elif self.settings.INTERPOLATION == 'CUBIC':
                return CubicTrajectoryPlanner()
            else:
                logging.error("trajectory planner not supported")
                return None
        else:
            logging.error("kinematic model not supported")
            return None

    def buildMovementSupervisor(self):
        supervisor = SupervisorContainer()
        return supervisor

    def buildTrajectoryTracker(self):
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            # TODO:Add if for selecting tracker
            if True:
                return IOLinearizationTrajectoryTracker(self.parameters)
            else:
                logging.error("trajectory tracker not supported")
                return None
        else:
            logging.error("kinematic model not supported")
            return None

    def buildMotorHandler(self):
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            if self.settings.FILENAME == 'VirtualMD.py':
                from robot.motion.MotorHandler.MotorDriver.Board.VirtualMD import VirtualMotorDriver
                speed_motor_driver = VirtualMotorDriver(
                    self.parameters.steps_per_revolution, self.parameters.max_speed)
                return HardSpeedControlledMH(speed_motor_driver)
            if self.settings.FILENAME == 'ArduinoMD.py':
                from robot.motion.MotorHandler.MotorDriver.Board.ArduinoMD import Arduino
                speed_motor_driver = Arduino(self.settings.MAX_SPEED)
                speed_motor_driver.set_constants(self.parameters.constant_kc, self.parameters.constant_ki,
                                                 self.parameters.constant_kd)
                return HardSpeedControlledMH(speed_motor_driver)
            elif self.settings.FILENAME == 'MD25.py':
                from robot.motion.MotorHandler.MotorDriver.Board.MD25 import MD25MotorDriver
                speed_controller = PIDSpeedController(self.parameters.constant_kc, self.parameters.constant_ki,
                                                      self.parameters.constant_kd, self.parameters.max_value_power,
                                                      self.parameters.min_value_power)
                power_motor_driver = MD25MotorDriver(1, 0x58)
                return SoftSpeedControlledMH(speed_controller, power_motor_driver)
            else:
                logging.error("motor driver not supported")
                return None
        else:
            logging.error("kinematic model not supported")
            return None

    def buildTimer(self):
        # load platform specific timer
        return DefaultTimer(self.settings.SAMPLE_TIME)

    def buildRobotParameters(self):
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            return DifferentialDriveRobotParameters(self.settings.RADIUS,
                                                    self.settings.DISTANCE,
                                                    self.settings.ENCODER_STEPS,
                                                    self.settings.CONST_B,
                                                    self.settings.CONST_K1,
                                                    self.settings.CONST_K2,
                                                    self.settings.CONST_KI,
                                                    self.settings.CONST_KD,
                                                    self.settings.CONST_KC,
                                                    self.settings.MAX_POWER_BIN,
                                                    -self.settings.MAX_POWER_BIN,
                                                    self.settings.SAMPLE_TIME,
                                                    self.settings.MAX_SPEED)

        else:
            logging.error("kinematic model not supported")
            return None

    def buildPlanner(self):
        planner = Planner()
        planner.map = "Gustavo's House"
        return planner


class Robot:
    __metaclass__ = Singleton

    def __init__(self):
        self.setting_handler = SettingHandler()
        self.motion = self.setting_handler.buildMovementControllers()
        self.planner = self.setting_handler.buildPlanner()

    def go_to(self, x, y, t):
        """
        Allows the robot to go from the current position
        to a given point in time t.

        Example:

        >>> r = Robot()
        >>> r.go_to(3, 4, 10) # Goes to (3,4) in 10s
        """

        trajectory = DifferentialDriveTrajectoryParameters(
            (DifferentialDriveRobotLocation(*self.position()),
             DifferentialDriveRobotLocation(x, y, 0.)),
            t, self.motion.robot_parameters.sample_time)

        self.track(trajectory)

    def go_to_with_planner(self, x, y, t):
        points = self.planner.get_points(start=self.position(), end=(x, y))
        self.follow(points, t)

    def follow(self, points, t):
        """
        Allows the robot to follow a set of given points in time t * len(points).

        Example:

        >>> r = Robot() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
                PROFILE: ...
        >>> trajectory = [(1,2), (6,1), (0,0)]
        >>> t = 10
        >>> r.follow(trajectory, t) # doctest: +ELLIPSIS
        """

        locations = [DifferentialDriveRobotLocation(
            p[0], p[1], 0.) for p in points]
        pos = self.position()
        locations.insert(0, DifferentialDriveRobotLocation(pos[0], pos[1], 0))

        trajectory = DifferentialDriveTrajectoryParameters(locations,
                                                           t, self.motion.robot_parameters.sample_time)

        self.track(trajectory)

    def track(self, trajectory_parameters):
        self.motion.movement_init(trajectory_parameters)
        self.motion.movement_start()

    def start_open_loop_control(self):
        self.motion.movement_init()
        self.motion.movement_start()

    def add_movement(self, direction):
        self.motion.dir = direction

    def stop_open_loop_control(self):
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

        >>> r = Robot() # doctest: +ELLIPSIS
        >>> r.position(2,3,0.5)
        >>> r.position()
        (2, 3, 0.5)
        """
        #---- get position ----
        if x is y is theta is None:
            x = self.motion.odometry_localizer.globalLocation.x_position
            y = self.motion.odometry_localizer.globalLocation.y_position
            z = self.motion.odometry_localizer.globalLocation.z_position
            return x, y, z

        #---- set position ----
        self.motion.odometry_localizer.globalLocation.x_position = x
        self.motion.odometry_localizer.globalLocation.y_position = y
        self.motion.odometry_localizer.globalLocation.z_position = theta

    def supervisor(self):
        return self.motion.movement_supervisor

    def change_supervisor(self, newsupervisor):
        self.motion.movement_supervisor = newsupervisor

    def change_trajectory_planner(self, newplanner):
        self.motion.trajectory_planner = newplanner

    def maps(self):
        return (map['name'] for map in self.planner.maps())

    def get_map(self, name):
        return self.planner.get_map(name) if name else self.planner.map

    def use_map(self, map_name):
        self.planner.use_map(map_name)
