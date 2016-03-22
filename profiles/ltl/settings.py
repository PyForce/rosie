"""
Settings
"""
# Configure the way rOSi handles your robot.

"""
Appearance
"""

# Name of the mobile robot
MOBILE_ROBOT = 'LTL2.0'

# Distance between the wheels (in meters)
DISTANCE = 0.30

# Radius of the wheels (in meters)
RADIUS = 0.04911


"""
Motor Controller
"""

# Filename of the controller board (this file is located in the folder: robot/board)
FILENAME = 'ArduinoMD.py'

# PID settings (Set it True if your hardware support speed control)
PID = True

# PID constants
CONST_KC = 3.75
CONST_KI = 1.25
CONST_KD = 1.25

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



"""
Future
"""

#
#        "processor" : "RaspberryPi",
#        "motor_controller" : "Arduino Uno",
#        "size" : [0.3, 0.5, 0.34],
#        "photo": "http://photo_url",
#        "sensors": ["seensor1", "sensor2"]
