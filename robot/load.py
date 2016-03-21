# -*- coding: utf-8 -*-

__all__=['SETTINGS','load_global_settings']

#### IMPORT ####

import os
import settings as global_settings

SETTINGS=None

def load_global_settings():
    """
    Load the robot's profile defined in the global settings.
    """
    global SETTINGS
    if os.path.exists(os.path.join(os.getcwd(),'profiles',global_settings.PROFILE)):
        try:
            exec("from profiles."+global_settings.PROFILE+" import settings")
            SETTINGS=locals()['settings']
            print('    PROFILE: '+global_settings.PROFILE)
        except:
            SETTINGS=None
            print("    ERROR! In <"+global_settings.PROFILE+">")
    else:
        print("    WARNING! Directory <"+global_settings.PROFILE+"> do not exist")