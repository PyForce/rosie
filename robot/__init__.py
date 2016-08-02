import os
import settings as global_settings

from robot.motion.Localizer.Method.RungeKutta import RungeKutta2OdometryLocalizer
from robot.motion.MotorHandler.Differential import HardSpeedControlledMH
from robot.motion.MotorHandler.Differential import SoftSpeedControlledMH
from robot.motion.MotorHandler.MotorDriver.Board.VirtualMD import VirtualMotorDriver
from robot.motion.MotorHandler.MotorDriver.Board.MD25 import MD25MotorDriver
from robot.motion.MovementController.Differential import DifferentialDriveRobotParameters, \
    DifferentialDriveMovementController, \
    DifferentialDriveRobotLocation
from robot.motion.MotorHandler.SpeedController.Controller.PID import PIDSpeedController
from robot.motion.MovementSupervisor.Supervisor.FileLogger import FileLoggerMovementSupervisor
from robot.motion.TrajectoryPlanner.Differential import DifferentialDriveTrajectoryParameters
from robot.motion.TrajectoryPlanner.Planner.Cubic import CubicTrajectoryPlanner
from robot.motion.TrajectoryPlanner.Planner.Linear import LinearTrajectoryPlanner
from robot.motion.TrajectoryTracker.Tracker.IOLinearization import IOLinearizationTrajectoryTracker
from tools.FileNameProvider import FileNameProviderByTime


class SettingHandler:
    def __init__(self):
        if os.path.exists(os.path.join(os.getcwd(), 'profiles', global_settings.PROFILE)):
            try:
                _temp = __import__("profiles.%s" % (global_settings.PROFILE),
                                   globals(), locals(), ['settings'], -1)
                self.settings = _temp.settings
                self.parameters = self.buildRobotParameters()
                print('    PROFILE: ' + global_settings.PROFILE)
            except:
                self.settings = None
                print("    ERROR! In <" + global_settings.PROFILE + ">")
        else:
            print("    ERROR! Directory <" + global_settings.PROFILE + "> do not exist")

    def buildMovementController(self):
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            return DifferentialDriveMovementController(self.buildMovementSupervisor(),
                                                       self.buildTrajectoryPlanner(),
                                                       self.buildLocalizer(),
                                                       self.buildTrajectoryTracker(),
                                                       self.buildMotorHandler(),
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
        if self.settings.KINEMATICS == 'DIFFERENTIAL':
            # TODO:Add if for selecting tracker
            if self.settings.SUPERVISOR == 'FILE_LOGGER':
                return FileLoggerMovementSupervisor(self.parameters, FileNameProviderByTime())
            else:
                print("    ERROR! Movement Supervisor Not Supported>")
                return None
        else:
            print("    ERROR! Kinematic Model Not Supported>")
            return None

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
            elif self.settings.FILENAME == 'MD25.py':
                speed_controller = PIDSpeedController(self.parameters.constant_kc, self.parameters.constant_ki,
                                                      self.parameters.constant_kd, self.parameters.max_value_power,
                                                      self.parameters.min_value_power)
                power_motor_driver = MD25MotorDriver(1, 0x58)
                return SoftSpeedControlledMH(speed_controller, power_motor_driver)
            else:
                print("    ERROR! Localizer Not Supported>")
                return None
        else:
            print("    ERROR! Kinematic Model Not Supported>")
            return None

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


class Robot:
    def __init__(self):
        self.setting_handler = SettingHandler()
        self.motion = self.setting_handler.buildMovementController()

    def track(self, trajectory_parameters):
        self.motion.movement_init(trajectory_parameters)
        self.motion.movement_start()

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



    def change_supervisor(self, newsupervisor):
        self.motion.movement_supervisor = newsupervisor

    def change_trajectory_planner(self, newplanner):
        self.motion.trajectory_planner = newplanner