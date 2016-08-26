from scanner import Scanner
from settings import config


scanner_server = Scanner(port=config.getint('scanner', 'port', 9876),
                         interval=config.getint('scanner', 'interval', 0))


def init():
    cluster_host = config.get('scanner', 'cluster-host', None)
    cluster_port = config.getint('scanner', 'cluster-port', 6789)
    if cluster_host:
        # send request to cluster host
        scanner_server.subscribe(cluster_host, cluster_port)

    if config.getboolean('scanner', 'scan', True):
        scanner_server.scan()


def end():
    scanner_server.stop()
