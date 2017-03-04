"""
Settings
"""
# Configure the way rOSi handles your robotOLD.

"""
Appearance
"""

# Name of the mobile robotOLD
MOBILE_ROBOT = 'SIMUBOT'

# Kinematic Model of the Robot
KINEMATICS = 'DIFFERENTIAL'

# Distance between the wheels (in meters)
DISTANCE = 0.2995

# Radius of the wheels (in meters)
RADIUS = 0.05

# Distance between the rear and the front part of the robotOLD (in meters)
LARGE = 0.20

# Distance between left and the right part of the robotOLD (in meters)
WIDTH = 0.42

# Distance between the floor and the highest part of the robotOLD (in meters)
HEIGHT = 0

"""
Motor Controller
"""

# Filename of the controller board (this file is located in the folder:
# robotOLD/board)
FILENAME = 'VirtualMD.py'

# PID settings (Set it True if your hardware support speed control)
PID = True

# PID constants
CONST_KC = 2.0
CONST_KI = 1.0
CONST_KD = 1.0

"""
Movement Controller
"""

# Trajectory planner interpolation method
INTERPOLATION = 'LINEAR'  # it can be LINEAR or CUBIC (so far)

# Localization method
LOCALIZER = 'ODOMETRY_RK2'

# Movement Supervisor Behavior
SUPERVISOR = 'FILE_LOGGER'

# Sample period
SAMPLE_TIME = 0.05

# Tracking Process constants
CONST_B = 0.1
CONST_K1 = 1.0
CONST_K2 = 1.0

"""
Motors
"""

# Resolution of encoders (In steps per turn)
ENCODER_STEPS = 360

# Max speed (in radians by seconds)
MAX_SPEED = 20.0

# Binary for controlling the fraction of power from the supply
MAX_POWER_BIN = 127.0

"""
Future
"""

#
#        "processor" : "RaspberryPi",
#        "motor_controller" : "Arduino Uno",
#        "size" : [0.3, 0.5, 0.34],
#        "photo": "http://photo_url",
#        "sensors": ["seensor1", "sensor2"]
