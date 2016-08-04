import hmac
import socket
import struct
import sys
from collections import namedtuple
from threading import Thread


if sys.version_info.major == 3:
    from http.client import HTTPConnection
else:
    from httplib import HTTPConnection


CHUNK_SIZE = 260

Client = namedtuple('Client', ['host', 'web', 'streaming'])
Cluster = namedtuple('Cluster', ['name', 'hot', 'port'])


class Scanner(Thread):
    def __init__(self, scan=True, **kwargs):
        namespace = kwargs.get('namespace')
        info = kwargs.get('info')
        host = kwargs.get('host')
        port = kwargs.get('port', 9876)

        if scan and namespace:
            self.socket = socket.socket(type=socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socker.bind(('', port))

            self.clusters = []
            enc_namespace = hmac.new(namespace).digest()
            data = struct.pack('!16s', enc_namespace)
            self.socket.sendto(data, ('<broadcast>', port))

            super(Scanner, self).__init__()

            self.start()
        elif host and info:
            # send request to cluster_host, cluster_port
            self.info = info
            self.subscribe(host, port)

    def run(self):
        while not self._Thread__stopped:
            data, (host, _) = self.socket.recvfrom(CHUNK_SIZE)
            port, name = struct.unpack('!hp', data)
            self.clusters.append(Cluster(name, host, port))

    def subscribe(self, host='', port=9876, cluster=None):
        if cluster:
            host = cluster.host
            port = cluster.port
        conn = HTTPConnection(host, port)
        conn.request('POST', "/subscribe?host=%s&web-port=%d&stream-port=%d" %
                    (self.info.host, self.info.web, self.info.streaming))
        return conn.getresponse().status == 200
