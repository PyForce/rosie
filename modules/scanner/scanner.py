import json
import socket
import struct
import sys
import threading
from collections import namedtuple

from settings import config
from utils import Singleton

if sys.version_info.major == 3:
    from http.client import HTTPConnection
else:
    from httplib import HTTPConnection


Cluster = namedtuple('Cluster', ['name', 'host', 'port'])


class Scanner:
    __metaclass__ = Singleton

    def __init__(self, **kwargs):
        # anything lower than 0 scan until stop is called
        self.interval = kwargs.get('interval', 5)
        self.port = kwargs.get('port', 9876)

        self.scan_struct = struct.Struct('!BB')
        self.recv_struct = struct.Struct('!BBhB')

        self.scanning = False

    def scan(self):
        if not self.scanning:
            self.socket = socket.socket(type=socket.SOCK_DGRAM,
                                        proto=socket.IPPROTO_UDP)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socket.settimeout(self.interval / 2
                                   if self.interval > 0 else 1)
            self.socket.bind(('', 0))

            data = self.scan_struct.pack(8, 0)
            self.socket.sendto(data, ('<broadcast>', self.port))

            self.scanning = True

            self.clusters = set()
            self.thread = threading.Thread(target=self.ping)
            self.thread.start()
            self.timer = self.interval > 0 and\
                threading.Timer(self.interval, self.stop)

    def stop(self):
        if self.scanning:
            self.timer and self.timer.cancel()
            self.scanning = False
            self.thread.join()
            self.socket.close()

    def ping(self):
        while self.scanning:
            try:
                data, (host, _) = self.socket.recvfrom(1024)
            except socket.timeout:
                break
            tp, msg, port, name_len = self.recv_struct.unpack(
                data[:self.recv_struct.size])
            if tp == msg == 0:
                name, = struct.unpack('!%ds' % name_len,
                                      data[self.recv_struct.size:])
            self.clusters.add(Cluster(name, host, port))

    def subscribe(self, host='', port=6789, cluster=None, **kwargs):
        if cluster:
            host = cluster.host
            port = cluster.port

        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'host': config.get('general', 'host', socket.gethostname()),
            'services': {
                sect: config.getint(sect, 'port')
                for sect in config.sections()
                if sect not in ('general', 'scanner') and
                config.has_option(sect, 'port')
            }
        }
        data['services'].update(kwargs)
        payload = json.dumps(data)

        conn = HTTPConnection(host, port)
        conn.request('POST', '/subscribe', payload, headers)
        # return if new resource was created
        return conn.getresponse().status == 201
