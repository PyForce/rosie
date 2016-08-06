from modules import kernel
from scanner import Scanner


scanner = None


def run():
    global scanner
    settings = kernel.ROBOT.profile()
    scanner = Scanner(scan=settings.get('SCANNER_SCAN', False),
                      info=settings.get('SCANNER_INFO'),
                      host=settings.get('SCANNER_HOST'))


def stop():
    scanner.stop()
