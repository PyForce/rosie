from time import sleep
from MRobot.RobotLocation import DifferentialDriveRobotLocation
from MRobot.TrajectoryParameters import DifferentialDriveTrajectoryParameters
from MRobot.FileNameProvider import FileNameProviderByTime
from MRobot.MotorDriver import MD25MotorDriver
from MRobot.MotorHandler import SpeedControllerMotorHandler
from MRobot.MovementController import DifferentialDriveMovementController
from MRobot.MovementSupervisor import FileLoggerMovementSupervisor
from MRobot.OdometryLocalizer import RungeKutta2OdometryLocalizer
from MRobot.RobotParameters import DifferentialDriveRobotParameters
from MRobot.SpeedController import PIDSpeedController
from MRobot.TrajectoryPlanner import LinearTrajectoryPlanner
from MRobot.TrajectoryTracker import IOLinearizationTrajectoryTracker

__author__ = 'Silvio'

if __name__ == '__main__':
    robot_parameters = DifferentialDriveRobotParameters(0.05, 0.2995, 360, 0.05, 3.0, 3.0, 1.0, 1.0, 2.0, 127.0, -128.0,
                                                        0.05)
    movement_supervisor = FileLoggerMovementSupervisor(robot_parameters, FileNameProviderByTime())
    trajectory_planner = LinearTrajectoryPlanner()
    odometry_localizer = RungeKutta2OdometryLocalizer(robot_parameters)
    trajectory_tracker = IOLinearizationTrajectoryTracker(robot_parameters.constant_b, robot_parameters.constant_k1,
                                                          robot_parameters.constant_k2, robot_parameters)
    speed_controller = PIDSpeedController(robot_parameters.constant_kc, robot_parameters.constant_ki,
                                          robot_parameters.constant_kd, robot_parameters.max_value_power,
                                          robot_parameters.min_value_power)
    power_motor_driver = MD25MotorDriver(1, 0x58)
    motor_handler = SpeedControllerMotorHandler(speed_controller, power_motor_driver)
    movement_controller = DifferentialDriveMovementController(movement_supervisor, trajectory_planner,
                                                              odometry_localizer,
                                                              trajectory_tracker, motor_handler, robot_parameters,
                                                              robot_parameters.sample_time)
    trajectory_parameters = DifferentialDriveTrajectoryParameters((DifferentialDriveRobotLocation(0., 0., 0.),
                                                                   DifferentialDriveRobotLocation(1., 0., 0.),
                                                                   DifferentialDriveRobotLocation(1., 1., 0.)), 5.,
                                                                  robot_parameters.sample_time)
    movement_controller.movement_init(trajectory_parameters)

    movement_controller.movement_start()

    while True:
        sleep(2)
