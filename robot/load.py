# -*- coding: utf-8 -*-
import settings.config as global_settings

__all__=['SETTINGS','load_global_settings']

#### IMPORT ####

import os

SETTINGS = None


def load_global_settings():
    """
    Load the robot's profile defined in the global settings.
    """
    global SETTINGS
    profile = global_settings.get('general', 'profile')
    if os.path.exists(os.path.join(os.getcwd(), 'profiles', profile)):
        try:
            # substitute dirty exec call
            _temp = __import__("profiles.%s" % (global_settings.PROFILE),
                               globals(), locals(), ['settings'], -1)
            SETTINGS = _temp.settings
            print('    PROFILE: '+global_settings.PROFILE)
        except:
            SETTINGS = None
            print("    ERROR! In <"+global_settings.PROFILE+">")
    else:
        print("    WARNING! Directory <"+profile+"> do not exist")
