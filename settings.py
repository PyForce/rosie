import sys
if sys.version_info.major == 3:
    import configparser
else:
    import ConfigParser as configparser


class FallbackConfigParser(configparser.ConfigParser, object):

    def get(self, section, option, fallback=None):
        if self.has_section(section) and self.has_option(section, option):
            return super(FallbackConfigParser, self).get(section, option)
        else:
            return fallback

    def getint(self, section, option, fallback=None):
        if self.has_section(section) and self.has_option(section, option):
            return super(FallbackConfigParser, self).getint(section, option)
        else:
            return fallback

    def getfloat(self, section, option, fallback=None):
        if self.has_section(section) and self.has_option(section, option):
            return super(FallbackConfigParser, self).getfloat(section, option)
        else:
            return fallback

    def getboolean(self, section, option, fallback=None):
        if self.has_section(section) and self.has_option(section, option):
            return super(FallbackConfigParser, self).getboolean(section,
                                                                option)
        else:
            return fallback

config = FallbackConfigParser(defaults={'active': 'False', 'logfile': None, 'loglevel': 'INFO',
                                        'profile': 'simubot'})
read = config.read('config.ini')
if 'config.ini' not in read:
    with open('config.ini', 'w+') as fp:
        del config.defaults()['active']
        _tmp, configparser.DEFAULTSECT = configparser.DEFAULTSECT, 'general'
        config.write(fp)
        configparser.DEFAULTSECT = _tmp
        config.defaults()['active'] = 'False'
        fp.seek(0)
        config.readfp(fp)
