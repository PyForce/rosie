import os
import sys

from settings import config as global_settings

from robot.motion.Localizer.Method.RungeKutta import RungeKutta2OdometryLocalizer
from robot.motion.MotorHandler.Differential import HardSpeedControlledMH
from robot.motion.MotorHandler.Differential import SoftSpeedControlledMH
from robot.motion.MotorHandler.MotorDriver.Board.VirtualMD import VirtualMotorDriver
from robot.motion.MotorHandler.MotorDriver.Board.MD25 import MD25MotorDriver
from robot.motion.MotorHandler.MotorDriver.Board.ArduinoMD import Arduino
from robot.motion.MovementController.Differential import DifferentialDriveRobotParameters, \
    DifferentialDriveMovementController, \
    DifferentialDriveRobotLocation
from robot.motion.MotorHandler.SpeedController.Controller.PID import PIDSpeedController
from robot.motion.TrajectoryPlanner.Differential import DifferentialDriveTrajectoryParameters
from robot.motion.TrajectoryPlanner.Planner.Cubic import CubicTrajectoryPlanner
from robot.motion.TrajectoryPlanner.Planner.Linear import LinearTrajectoryPlanner
from robot.motion.TrajectoryTracker.Tracker.IOLinearization import IOLinearizationTrajectoryTracker
from robot.motion.MovementTimer import UnixTimer, WindowsTimer
from robot.motion.MovementSupervisor.Differential import SupervisorContainer


from tools.singleton import Singleton
from planning.planner import Planner


class SettingHandler:
    def __init__(self):
        self.profile = global_settings.get('general', 'profile')
        if os.path.exists(os.path.join(os.getcwd(), 'profiles', self.profile)):
            try:
                _temp = __import__("profiles.%s" % (self.profile),
                                   globals(), locals(), ['settings'], -1)
                self.settings = _temp.settings
                self.parameters = self.buildRobotParameters()
                print('    PROFILE: ' + self.profile)
            except:
                self.settings = None
                print("    ERROR! In <" + self.profile + ">")
        else:
            print("    ERROR! Directory <" + self.profile + "> do not exist")

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
            print("    ERROR! Kinematic Model Not Supported>")
            return None

    def buildLocalizer(self):
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            if self.settings.LOCALIZER == 'ODOMETRY_RK2':
                return RungeKutta2OdometryLocalizer(self.parameters)
            else:
                print("    ERROR! Localizer Not Supported>")
                return None
        else:
            print("    ERROR! Kinematic Model Not Supported>")
            return None

    def buildTrajectoryPlanner(self):
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            if self.settings.INTERPOLATION == 'LINEAR':
                return LinearTrajectoryPlanner()
            elif self.settings.INTERPOLATION == 'CUBIC':
                return CubicTrajectoryPlanner()
            else:
                print("    ERROR! Trajectory Planner Not Supported>")
                return None
        else:
            print("    ERROR! Kinematic Model Not Supported>")
            return None

    def buildMovementSupervisor(self):
        supervisor = SupervisorContainer()
        # if self.settings.KINEMATICS == 'DIFFERENTIAL':
        #     # TODO:Add if for selecting tracker
        #     if self.settings.SUPERVISOR == 'FILE_LOGGER':
        #         supervisor.append(FileLoggerMovementSupervisor(self.parameters,
        #                           FileNameProviderByTime()))
        #     else:
        #         print("    ERROR! Movement Supervisor Not Supported>")
        #         return None
        # else:
        #     print("    ERROR! Kinematic Model Not Supported>")
        #     return None
        return supervisor

    def buildTrajectoryTracker(self):
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            # TODO:Add if for selecting tracker
            if True:
                return IOLinearizationTrajectoryTracker(self.parameters)
            else:
                print("    ERROR! Trajectory Tracker Not Supported>")
                return None
        else:
            print("    ERROR! Kinematic Model Not Supported>")
            return None

    def buildMotorHandler(self):
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            if self.settings.FILENAME == 'VirtualMD.py':
                speed_motor_driver = VirtualMotorDriver(self.parameters.steps_per_revolution, self.parameters.max_speed)
                return HardSpeedControlledMH(speed_motor_driver)
            if self.settings.FILENAME == 'ArduinoMD.py':
                speed_motor_driver = Arduino(self.settings.MAX_SPEED)
                speed_motor_driver.set_constants(self.parameters.constant_kc, self.parameters.constant_ki,
                                                      self.parameters.constant_kd)
                return HardSpeedControlledMH(speed_motor_driver)
            elif self.settings.FILENAME == 'MD25.py':
                speed_controller = PIDSpeedController(self.parameters.constant_kc, self.parameters.constant_ki,
                                                      self.parameters.constant_kd, self.parameters.max_value_power,
                                                      self.parameters.min_value_power)
                power_motor_driver = MD25MotorDriver(1, 0x58)
                return SoftSpeedControlledMH(speed_controller, power_motor_driver)
            else:
                print("    ERROR! Motor Driver Not Supported>")
                return None
        else:
            print("    ERROR! Kinematic Model Not Supported>")
            return None

    def buildTimer(self):
        if sys.platform.startswith("win"):
            # Use Windows base system driver
            return WindowsTimer(self.settings.SAMPLE_TIME)
        else:
            # Use Unix based system driver
            return UnixTimer(self.settings.SAMPLE_TIME)

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
            print("    ERROR! Kinematic Model Not Supported>")
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

    def track(self, trajectory_parameters):
        self.motion.movement_init(trajectory_parameters)
        self.motion.movement_start()

    def start_open_loop_control(self):
        self.motion.movement_init(None)
        self.motion.movement_start()

    def add_key_list(self, keys):
        self.motion.keys = keys

    def stop_open_loop_control(self):
        self.motion.movement_finish()

    def position(self,x=None,y=None,theta=None):
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
        #---- get position ----
        if x == None and y == None and theta == None:
            x = self.motion.odometry_localizer.globalLocation.x_position
            y = self.motion.odometry_localizer.globalLocation.y_position
            z = self.motion.odometry_localizer.globalLocation.z_position
            return x, y, z

        # TODO: Check the invertion
        #---- set position ----
        self.motion.odometry_localizer.globalLocation.y_position = x
        self.motion.odometry_localizer.globalLocation.x_position = y
        self.motion.odometry_localizer.globalLocation.z_position = theta

    def supervisor(self):
        return self.motion.movement_supervisor

    def change_supervisor(self, newsupervisor):
        self.motion.movement_supervisor = newsupervisor

    def change_trajectory_planner(self, newplanner):
        self.motion.trajectory_planner = newplanner
