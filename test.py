from time import sleep

from Motion.Localizer.Method.RungeKutta import RungeKutta2OdometryLocalizer
from Motion.MotorHandler.Differential import SoftSpeedControlledMH
from Motion.MotorHandler.MotorDriver.Board.MD25 import MD25MotorDriver
from Motion.MotorHandler.SpeedController.Controller.PID import PIDSpeedController
from Motion.MovementController.Differential import DifferentialDriveRobotParameters, \
    DifferentialDriveMovementController, \
    DifferentialDriveRobotLocation
from Motion.MovementSupervisor.Supervisor.FileLogger import FileLoggerMovementSupervisor
from Motion.TrajectoryPlanner.Differential import DifferentialDriveTrajectoryParameters
from Motion.TrajectoryPlanner.Planner.Linear import LinearTrajectoryPlanner
from Motion.TrajectoryTracker.Tracker.IOLinearization import IOLinearizationTrajectoryTracker

from Tools.FileNameProvider import FileNameProviderByTime

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
    motor_handler = SoftSpeedControlledMH(speed_controller, power_motor_driver)
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
