import threading

from .cluster import cluster_server, responder_server
from settings import config


def init():
    if config.getboolean('cluster', 'visible', True):
        responder_thread = threading.Thread(
            target=responder_server.serve_forever)
        responder_thread.start()

    cluster_server.serve_forever()


def end():
    if responder_server:
        responder_server.shutdown()
    if cluster_server:
        cluster_server.shutdown()
