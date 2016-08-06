import sys
if sys.version_info.major == 3:
    import configparser
else:
    import ConfigParser as configparser


config = configparser.ConfigParser(defaults={'active': False})
config.read('config')
