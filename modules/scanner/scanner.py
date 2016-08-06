import socket
import struct
import sys
import threading
from collections import namedtuple


if sys.version_info.major == 3:
    from http.client import HTTPConnection
else:
    from httplib import HTTPConnection


Client = namedtuple('Client', ['host', 'web', 'streaming'])
Cluster = namedtuple('Cluster', ['name', 'hot', 'port'])


class Scanner:
    def __init__(self, scan=True, **kwargs):
        info = kwargs.get('info')
        host = kwargs.get('host')
        # anything lower than 0 scan until stop is called
        self.interval = kwargs.get('interval', 5)
        self.port = kwargs.get('port', 9876)

        self.scan_struct = struct.Struct('!BB')
        self.recv_struct = struct.Struct('!BBhB')

        self.scanning = False

        if scan:
            self.scan()
        elif host and info:
            # send request to cluster_host, cluster_port
            self.info = info if isinstance(info, Client) else Client(**info)
            self.subscribe(host, self.port)

    def scan(self):
        if not self.scanning:
            self.socket = socket.socket(type=socket.SOCK_DGRAM,
                                        proto=socket.IPPROTO_UDP)
            self.socket.bind(('', self.port))

            data = self.scan_struct.pack(8, 0)
            self.socket.sendto(data, ('<broadcast>', self.port))

            self.scanning = True

            self.clusters = []
            self.thread = threading.Thread(target=self.ping)
            # close thread together with main thread
            self.thread.daemon = True
            self.thread.start()
            self.timer = self.interval > 0 and threading.Timer(self.interval,
                                                               self.stop)

    def stop(self):
        if self.scanning:
            self.timer and self.timer.cancel()
            self.scanning = False
            self.thread.join()
            self.socket.shutdown()

    def ping(self):
        while self.scanning:
            data, (host, _) = self.socket.recvfrom(1024)
            tp, msg, port, name_len = self.recv_struct.unpack(
                data[:self.recv_struct.size])
            if tp == msg == 0:
                name = struct.unpack('!%ds' % name_len,
                                     data[self.recv_struct.size:])
            self.clusters.append(Cluster(name, host, port))

    def subscribe(self, host='', port=6789, cluster=None):
        if cluster:
            host = cluster.host
            port = cluster.port
        conn = HTTPConnection(host, port)
        conn.request('POST', "/subscribe?host=%s&web-port=%d&stream-port=%d" %
                    (self.info.host, self.info.web, self.info.streaming))
        return conn.getresponse().status == 200
