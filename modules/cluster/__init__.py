import threading

responder_server = None
cluster_server = None

from .cluster import http_client, socketserver, ClusterHandler, ScanHandler
from settings import config


def init():
    global cluster_server, responder_server

    if config.getboolean('cluster', 'visible', True):
        host = config.get('cluster', 'visble-host', '')
        port = config.getint('cluster', 'visble-port', 9876)
        responder_server = socketserver.UDPServer((host, port), ScanHandler)

        responder_thread = threading.Thread(
            target=responder_server.serve_forever)
        # Exit the responder thread when the main thread terminates
        responder_thread.daemon = True
        responder_thread.start()

    host = config.get('cluster', 'host', '')
    port = config.getint('cluster', 'port', 6789)
    cluster_server = http_client.HTTPServer((host, port), ClusterHandler)

    cluster_thread = threading.Thread(target=cluster_server.serve_forever)
    cluster_thread.daemon = True
    cluster_thread.start()


def end():
    if responder_server:
        responder_server.shutdown()
    if cluster_server:
        cluster_server.shutdown()
