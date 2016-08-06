import threading

from cluster import http_client, socketserver, ClusterHandler, ScanHandler
from modules.kernel import kernel


def run():
    settings = kernel.ROBOT.profile()
    if settings.get('CLUSTER_VISIBLE'):
        responder_address = settings.get('CLUSTER_VISIBLE_BIND', ('', 9876))
        responder = socketserver.UDPServer(responder_address, ScanHandler)

        responder_thread = threading.Thread(target=responder.serve_forever)
        # Exit the responder thread when the main thread terminates
        responder_thread.daemon = True
        responder_thread.start()

    cluster_address = settings.get('CLUSTER_BIND', ('', 6789))
    cluster = http_client.HTTPServer(cluster_address, ClusterHandler)

    cluster_thread = threading.Thread(target=cluster.serve_forever)
    cluster_thread.daemon = True
    cluster_thread.start()
