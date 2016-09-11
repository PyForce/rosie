import re
import struct
import sys
import json
from settings import config

if sys.version_info.major == 3:
    import socketserver
    import http.client as http_client
else:
    import SocketServer as socketserver
    import BaseHTTPServer as http_client


class ScanHandler(socketserver.BaseRequestHandler):
    name = config.get('cluster', 'name', 'my-cluster')
    poke_struct = struct.Struct('!BB')
    info_struct = struct.Struct('!BBhB%ds' % len(name))

    def handle(self):
        data = self.request[0]
        socket = self.request[1]
        tp, msg = self.poke_struct.unpack(data)

        if tp == 8 and msg == 0:
            info = self.info_struct.pack(0, 0, cluster_server.server_port,
                                         len(self.name), self.name)
            socket.sendto(info, self.client_address)


class ClusterHandler(http_client.BaseHTTPRequestHandler):
    robots = {}

    def do_GET(self):
        if self.path == '/list':
            payload = json.dumps([{'host': host, 'services': self.robots[host]}
                                 for host in self.robots])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.wfile.write('\r\n')
            self.wfile.write(payload)

    unsubs_re = re.compile(r'/unsubscribe\?host=(?P<host>.*)')

    def do_POST(self):
        if self.path == '/subscribe':
            payload = self.rfile.read(int(self.headers['Content-Length']))
            try:
                info = json.loads(payload)
            except ValueError:
                self.send_error(400)
            else:
                if info['host'] in self.robots:
                    self.send_error(409,
                                    'A Robot with that host is already'
                                    ' registered')
                else:
                    self.robots[info['host']] = info['services']
                    self.send_response(201)

    def do_DELETE(self):
        match = self.unsubs_re.match(self.path)
        if match:
            host, = match.groups('host')
            if host in self.robots:
                del self.robots[host]
                self.send_response(204)
            else:
                self.send_error(404,
                                "The host doesn't match any registered robotOLD")


if config.getboolean('cluster', 'visible', True):
    host = config.get('cluster', 'visible-host', '')
    port = config.getint('cluster', 'visible-port', 9876)
    responder_server = socketserver.UDPServer((host, port), ScanHandler)

host = config.get('cluster', 'host', '')
port = config.getint('cluster', 'port', 6789)
cluster_server = http_client.HTTPServer((host, port), ClusterHandler)
