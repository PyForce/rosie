"""
Settings
"""
# Configure the way rOSi handles your robotOLD.

"""
Appearance
"""

# Name of the mobile robotOLD
MOBILE_ROBOT = 'LTL3.0'

# Kinematic Model of the Robot
KINEMATICS = 'DIFFERENTIAL'

# Distance between the wheels (in meters)
DISTANCE = 0.249

# Radius of the wheels (in meters)
RADIUS = 0.04911

# Distance between the rear and the front part of the robotOLD (in meters)
LARGE = 0.277

# Distance between left and the right part of the robotOLD (in meters)
WIDTH = 0.30

# Distance between the floor and the highest part of the robotOLD (in meters)
HEIGHT = 0.24

"""
Motor Controller
"""

# Filename of the controller board (this file is located in the folder:
# robotOLD/board)
FILENAME = 'ArduinoMD.py'

# PID settings (Set it True if your hardware support speed control)
PID = True

# PID constants
CONST_KC = 3.75
CONST_KI = 1.25
CONST_KD = 1.25

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
ENCODER_STEPS = 270.9

# Max speed (in radians by seconds)
MAX_SPEED = 8.0

# Binary for controlling the fraction of power from the supply
MAX_POWER_BIN = 0.0

"""
Streaming
"""

# uri of the video stream (start with ':' for same host and specify the port)
VIDEO_URI = ':8080/stream/video.mjpeg'

"""
Future
"""

#
#        "processor" : "RaspberryPi",
#        "motor_controller" : "Arduino Uno",
#        "size" : [0.3, 0.5, 0.34],
#        "photo": "http://photo_url",
#        "sensors": ["seensor1", "sensor2"]
