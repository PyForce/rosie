import Queue
import socket


class Server:
    def __init__(self, port, motion):
        self.motion = motion
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.queue = Queue.Queue()
        self.address = None

    def process_request(self, request):
        command, data = request.split(' ')
        if command == 'path':
            track_data = data.split(',')

            x_planning = []
            y_planning = []
            z_planning = []

            for i, string in enumerate(track_data[3:]):
                if i % 3 == 0:
                    x_planning.append(float(string))
                elif i % 3 == 1:
                    y_planning.append(float(string))
                else:
                    z_planning.append(float(string))

            track = {'constant_t': float(track_data[0]),
                     'constant_k': float(track_data[1]),
                     'cubic': True,
                     'x_planning': x_planning,
                     'y_planning': y_planning,
                     'z_planning': z_planning}
            if self.motion.finished:
                self.motion.experiment_init(track_data[2], False, track)
                self.queue.put('path begin')
            else:
                self.queue.put('experiment running')
        elif command == 'points':
            track_data = data.split(',')

            x_planning = []
            y_planning = []
            t_planning = []

            for i, string in enumerate(track_data[1:]):
                if i % 3 == 0:
                    x_planning.append(float(string))
                elif i % 3 == 1:
                    y_planning.append(float(string))
                else:
                    t_planning.append(float(string))

            track = {'x_planning': x_planning,
                     'y_planning': y_planning,
                     't_planning': t_planning}
            if self.motion.finished:
                self.motion.experiment_init(track_data[0], False, track)
                self.queue.put('points begin')
            else:
                self.queue.put('experiment running')
        elif command == 'reference':
            track_data = data.split(',')

            x_planning = []
            y_planning = []
            t_planning = []

            for i, string in enumerate(track_data[1:]):
                if i % 3 == 0:
                    x_planning.append(float(string))
                elif i % 3 == 1:
                    y_planning.append(float(string))
                else:
                    t_planning.append(float(string))

            track = {'x_planning': x_planning,
                     'y_planning': y_planning,
                     't_planning': t_planning}
            if self.motion.finished:
                self.motion.experiment_init(track_data[0], True, track)
                self.queue.put('reference begin')
            else:
                self.queue.put('experiment running')
        elif command == 'experiment':
            if data == 'stop':
                self.motion.finished = True
                self.queue.put('stop ok')
            else:
                self.queue.put('bad message')
        else:
            self.queue.put('bad message')

    def sender_thread(self):
        while 1:
            if not self.queue.empty():
                to_send = self.queue.get()
                self.socket.sendto(to_send, self.address)

    def run(self):
        while 1:
            request, address = self.socket.recvfrom(1024)
            self.address = address
            self.process_request(request)
            #print 'Request:[%s]' % request
            #self.socket.sendto(request, address)
