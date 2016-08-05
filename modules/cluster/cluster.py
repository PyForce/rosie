import re
import struct
import sys
from socket import inet_aton


if sys.version_info.major == 3:
    import socketserver
    import http.client as http_client
else:
    import SocketServer as socketserver
    import BaseHTTPServer as http_client


class ScanHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        socket = self.request[1]
        host_a, w_port, s_port = struct.unpack(data)
        # TODO: Fix paramenters to send
        info = struct.pack('!4shp', inet_aton(''), 0, 'My Cluster')
        socket.sendto(info, self.client_address)


class ClusterHandler(http_client.BaseHTTPRequestHandler):
    def do_GET(self):
        pass

    subs_re = re.compile(r'/subscribe\?host=(?P<host>[^&]*)&web-port=(?P<web>'
                         '[0-9]{1,5})&stream-port=(?P<stream>[0-9]{1,5})')

    def do_POST(self):
        subscribe = self.subs_re.match(self.path)
        if subscribe:
            pass
