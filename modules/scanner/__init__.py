from scanner import Scanner


scanner = None


def init():
    global scanner
    from settings import config

    listen = config.getint('scanner', 'port', 9876)
    scanner = Scanner(scan=config.getboolean('scanner', 'scan', True),
                      host=config.get('scanner', 'cluster_host', None),
                      port=config.getint('scanner', 'cluster_port', listen))


def end():
    scanner.stop()
