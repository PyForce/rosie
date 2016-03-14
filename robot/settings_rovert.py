"""
Settings
"""
# Configure the way rOSi handles your robot.

"""
Appearance
"""

# Name of the mobile robot
MOBILE_ROBOT = 'ROBERT'

# Distance between the wheels (in meters)
DISTANCE = 0.2995

# Radius of the wheels (in meters)
RADIUS = 0.05


"""
Motor Controller
"""

# Filename of the controller board (this file is located in the folder: robot/board)
FILENAME = 'MD25.py'

# PID settings (Set it True if your hardware support speed control)
PID = False


"""
Motors
"""

# Resolution of encoders (In steps per turn)
ENCODER_STEPS = 360

# Max speed (in radians by seconds)
MAX_SPEED = 12.0



"""
Future
"""

#
#        "processor" : "RaspberryPi",
#        "motor_controller" : "Arduino Uno",
#        "size" : [0.3, 0.5, 0.34],
#        "photo": "http://photo_url",
#        "sensors": ["seensor1", "sensor2"]
