from scanner import Scanner


scanner = None


def init():
    global scanner
    from settings import config

    scanner = Scanner(scan=config.getboolean('scanner', 'scan', True),
                      port=config.getint('scanner', 'port', 9876),
                      cluster_host=config.get('scanner', 'cluster-host', None),
                      cluster_port=config.getint('scanner', 'cluster-port',
                                                 6789))


def end():
    scanner.stop()
