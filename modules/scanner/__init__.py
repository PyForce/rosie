from scanner import Scanner
from settings import config


scanner_server = Scanner(port=config.getint('scanner', 'port', 9876),
                         interval=config.getint('scanner', 'interval', 0))


def init():



def end():
    scanner_server.stop()
