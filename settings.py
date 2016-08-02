"""
Settings
"""
# Setup the general settings of rOSi.

__all__=['PROFILE', 'MODULES']

import profiles

# Name of the robot's profile directory (this directory is located in the folder: profiles)
PROFILE = 'simubot'

# Modules to load
MODULES = profiles.WebHUD | profiles.ordex

# Log
LOG = False