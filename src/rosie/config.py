import configparser


class FallbackConfigParser(configparser.RawConfigParser):
    def get(self, section, option, **kwargs):
        if self.has_section(section) and self.has_option(section, option):
            return super().get(section, option)
        else:
            return kwargs.get("fallback", None)

    def getint(self, section, option, **kwargs):
        if self.has_section(section) and self.has_option(section, option):
            return super().getint(section, option)
        else:
            return kwargs.get("fallback", None)

    def getfloat(self, section, option, **kwargs):
        if self.has_section(section) and self.has_option(section, option):
            return super().getfloat(section, option)
        else:
            return kwargs.get("fallback", None)

    def getboolean(self, section, option, **kwargs):
        if self.has_section(section) and self.has_option(section, option):
            return super().getboolean(section, option, **kwargs)
        else:
            return kwargs.get("fallback", None)


config = FallbackConfigParser(
    defaults={"active": "False", "loglevel": "INFO", "profile": "simubot"}
)
read = config.read("config.ini")
if "config.ini" not in read:
    with open("config.ini", "w+") as fp:
        del config.defaults()["active"]
        _, configparser.DEFAULTSECT = configparser.DEFAULTSECT, "general"
        config.add_section("web")
        config.set("web", "active", True)
        config.write(fp)
        configparser.DEFAULTSECT = _
        config.defaults()["active"] = "False"
        fp.seek(0)
        config.read_file(fp)
