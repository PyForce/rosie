import importlib
import os
import signal
import sys
import threading
import traceback

from modules import kernel
from settings import config
from robot import Robot


from robot.motion.MovementController.Differential import\
    DifferentialDriveRobotLocation
from robot.motion.MovementSupervisor.Differential\
    import DifferentialDriveMovementSupervisor
from robot.motion.TrajectoryPlanner.Differential import\
    DifferentialDriveTrajectoryParameters
from robot.motion.TrajectoryPlanner.Planner.Linear import\
    LinearTrajectoryPlanner
from robot.motion.TrajectoryPlanner.Planner.Cubic import\
    CubicTrajectoryPlanner

import matplotlib.pyplot as plt 


sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'modules')))


import numpy as np
import time 

r = Robot()

r.go_to(1,1,5)
for i in range(5):
    pos = r.position()
    print(pos)
    plt.scatter(pos[0],pos[1])
    time.sleep(1)

x = [element.x_position for element in r.motion.trajectory_planner.reference_locations]
y = [element.y_position for element in r.motion.trajectory_planner.reference_locations]
plt.plot(x, y)
plt.show()

print("")
r.go_to(1,1,5)
for i in range(10):
    pos = r.position()
    print(pos)
    plt.scatter(pos[0],pos[1])
    time.sleep(0.5)

x = [element.x_position for element in r.motion.trajectory_planner.reference_locations]
y = [element.y_position for element in r.motion.trajectory_planner.reference_locations]
plt.plot(x, y)
plt.show()
# trajectory = [(1,2), (6,1), (1,0)]
# t = 10
# r.follow(trajectory, t)

# for i in range((len(trajectory)) * t + 1):
# 	pos = r.position()
# 	print(pos)
# 	plt.scatter(pos[0],pos[1])
# 	time.sleep(1)

# x  = [element.x_position for element in r.motion.trajectory_planner.reference_locations]
# y  = [element.y_position for element in r.motion.trajectory_planner.reference_locations]

# plt.plot(x,y)
# plt.show()



# print(r.position())
# t = 5

# trajectory = ( \
# 			DifferentialDriveRobotLocation(0., 0., 0.),
#             DifferentialDriveRobotLocation(1., 2., 0.),
#             DifferentialDriveRobotLocation(6., 1., 0.),
#             DifferentialDriveRobotLocation(0., 0., 0.)
#             )


# trajectory_parameters = DifferentialDriveTrajectoryParameters(
#             trajectory, t, r.motion.robot_parameters.sample_time)

# r.track(trajectory_parameters)




# ##### TODO: Quitar

# # b = r.motion.trajectory_planner.reference_speeds

# # print(a,b)
# #####