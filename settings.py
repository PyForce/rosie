import sys
if sys.version_info.major == 3:
    import configparser
else:
    import ConfigParser as configparser


class FallbackConfigParser(configparser.ConfigParser, object):

    def get(self, section, option, **kwargs):
        if self.has_section(section) and self.has_option(section, option):
            return super(FallbackConfigParser, self).get(section, option)
        else:
            return kwargs.get('fallback', None)

    def getint(self, section, option, **kwargs):
        if self.has_section(section) and self.has_option(section, option):
            return super(FallbackConfigParser, self).getint(section, option)
        else:
            return kwargs.get('fallback', None)

    def getfloat(self, section, option, **kwargs):
        if self.has_section(section) and self.has_option(section, option):
            return super(FallbackConfigParser, self).getfloat(section, option)
        else:
            return kwargs.get('fallback', None)

    def getboolean(self, section, option, **kwargs):
        if self.has_section(section) and self.has_option(section, option):
            return super(FallbackConfigParser, self).getboolean(section,
                                                                option,
                                                                **kwargs)
        else:
            return kwargs.get('fallback', None)

config = FallbackConfigParser(defaults={'active': 'False', 'loglevel': 'INFO',
                                        'profile': 'simubot'})
read = config.read('config.ini')
if 'config.ini' not in read:
    with open('config.ini', 'w+') as fp:
        del config.defaults()['active']
        _, configparser.DEFAULTSECT = configparser.DEFAULTSECT, 'general'
        config.add_section("restAPI")
        config.set("restAPI", "active", True)
        config.write(fp)
        configparser.DEFAULTSECT = _
        config.defaults()['active'] = 'False'
        fp.seek(0)
        config.readfp(fp)
