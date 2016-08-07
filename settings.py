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

config = FallbackConfigParser(defaults={'active': 'False', 'log': 'False'})
config.read('config')
