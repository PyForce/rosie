"""
rOSi settings for app.
"""

# Name of the mobile robot
MOBILE_ROBOT = 'ROBERT'

# Filename of board (this file is located in the folder: robot/board)
FILENAME = 'robert.py'

# PID settings for control of motors
PID = False



ENCODER_STEPS = 360

# Distance between the wheels (in meters)
DISTANCE = 0.2995

# Radius of the wheels (in meters)
RADIUS = 0.05

# Max speed (in radians by seconds)
MAX_SPEED = 8.0


#
#        "processor" : "RaspberryPi",
#        "motor_controller" : "Arduino Uno",
#        "size" : [0.3, 0.5, 0.34],
#        "photo": "http://photo_url",
#        "sensors": ["seensor1", "sensor2"]