import re
import struct
import sys
import json
from . import cluster
from modules import kernel

if sys.version_info.major == 3:
    import socketserver
    import http.client as http_client
else:
    import SocketServer as socketserver
    import BaseHTTPServer as http_client


class ScanHandler(socketserver.BaseRequestHandler):
    name = kernel.ROBOT.profile().get('CLUSTER_NAME', 'my-cluster')
    poke_struct = struct.Struct('!BB')
    info_struct = struct.Struct('!BBhB%ds' % len(name))

    def handle(self):
        data = self.request[0]
        socket = self.request[1]
        tp, msg = self.poke_struct.unpack(data)

        if tp == 8 and msg == 0:
            info = self.info_struct.pack(0, 0, cluster.server_port,
                                         len(self.name), self.name)
            socket.sendto(info, self.client_address)


class ClusterHandler(http_client.BaseHTTPRequestHandler):
    robots = {}

    def do_GET(self):
        pass


    def do_POST(self):
        if self.path == '/subscribe':
            payload = self.rfile.read(self.headers['Content-Length'])
            info = json.loads(payload)
            if info['host'] in self.robots:
                self.send_error(409,
                                'A Robot with that host is already registered')
            else:
                self.robots[info['host']] = info['services']
                self.send_response(200)
