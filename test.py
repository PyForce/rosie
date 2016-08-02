from time import sleep
from robot import Robot
from robot.motion.MovementController.Differential import DifferentialDriveRobotLocation
from robot.motion.TrajectoryPlanner.Differential import DifferentialDriveTrajectoryParameters

if __name__ == '__main__':
    r = Robot()

    trajectory_parameters = DifferentialDriveTrajectoryParameters((DifferentialDriveRobotLocation(0., 0., 0.),
                                                                   DifferentialDriveRobotLocation(1., 0., 0.),
                                                                   DifferentialDriveRobotLocation(1., 1., 0.)), 5.,
                                                                   r.motion.sample_time)
    r.track(trajectory_parameters)

    while True:
        sleep(2)
