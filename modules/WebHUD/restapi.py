import os

from flask import request, jsonify, json, url_for, send_file
from kernel import handler as robot_handler

from . import app, sio
from .utils import allow_origin
from settings import config
from scanner import scanner_server as scanner
from robotNew.motion.MovementSupervisor.Differential\
    import DifferentialDriveMovementSupervisor
from robotNew import Robot


client_count = 0


@app.route('/odometry', methods=['GET'])
@allow_origin
def odometry():
    """
    {
        "x": 2.1,
        "y": 1.3,
        "theta": 3.21
    }
    """
    x, y, theta = robot_handler.get_odometry()
    return jsonify(x=x, y=y, theta=theta)


@app.route('/profile', methods=['GET'])
@allow_origin
def profile():
    """
    {
        "x": 2.1,
        "y": 1.3,
        "theta": 3.21
    }
    """
    prof = robot_handler.get_profile()
    return jsonify(prof=prof)


@app.route('/metadata', methods=['GET'])
@allow_origin
def metadata():
    settings = robot_handler.kernel.ROBOT.profile()
    data = {
        "name": settings['MOBILE_ROBOT'],
        "thumbnail": url_for('.thumbnail'),
        "vector": url_for('.vector'),
        "size": [settings['LARGE'], settings['WIDTH'], settings['HEIGHT']]
    }
    return jsonify(**data)


@app.route('/thumbnail', methods=['GET'])
@allow_origin
def thumbnail():
    profile = config.get('general', 'profile')
    filePath = os.path.join(os.getcwd(), 'profiles', profile, 'thumbnail.png')
    return send_file(filePath)


@app.route('/vector', methods=['GET'])
@allow_origin
def vector():
    profile = config.get('general', 'profile')
    filePath = os.path.join(os.getcwd(), 'profiles', profile, 'vector.svg')
    return send_file(filePath)


@app.route('/sensor/<string:name>', methods=['GET'])
@allow_origin
def sensor(name):
    """
    {
        "name": %s
    }
    """
    return jsonify(**json.loads(sensor.__doc__ % name))


@app.route('/position', methods=['PUT'])
@allow_origin
def position():
    """
    {
        "x": x,
        "y": y,
        "theta": theta
    }
    """
    x = request.values['x']
    y = request.values['y']
    theta = request.values['theta']
    robot_handler.set_position(x, y, theta)
    return 'OK'


@app.route('/path', methods=['PUT'])
@allow_origin
def path():
    """
    {
        "path": [(x, y), (x, y), ... ]
    }
    """
    path = request.values['path']
    path = json.loads(path)
    robot_handler.set_path(path)
    return 'OK'


@app.route('/text', methods=['PUT'])
@allow_origin
def text():
    """
    {
        "text": "some text"
    }
    """
    text = str(request.values['text'])
    robot_handler.process_text(text)
    return 'OK'


@app.route('/maps', methods=['PUT'])
@allow_origin
def maps():
    """
    {
        "map": "map_name"
    }
    """
    map = request.values['map']
    return 'OK'


@app.route('/clusters')
@allow_origin
def clusters():
    data = {
        cluster.name: [cluster.host, cluster.port]
        for cluster in scanner.clusters
    }
    return jsonify(**data)


class WebHUDMovementSupervisor(DifferentialDriveMovementSupervisor):
    def __init__(self, sio, robot):
        self.robot = robot
        self.sio = sio
        self.keys = []
        # use old-style decorators to subscribe bounded methods
        sio.on('manual')(self.drive_manual)  # key press
        app.route('/auto_mode', methods=['PUT'])(allow_origin(self.auto_mode))
        app.route('/manual_mode', methods=['PUT'])(allow_origin(
            self.manual_mode))

    def movement_begin(self, *args, **kwargs):
        pass

    def movement_end(self, *args, **kwargs):
        pass

    def movement_update(self, state):
        if self.manual:
            # update keys
            self.robot.add_key_list(self.keys)
        x, y, theta = state.global_location.x_position,\
            state.global_location.y_position, state.global_location.z_position
        self.sio.emit('position', {'x': -y, 'y': x, 'theta': theta})

    def drive_manual(self, data):
        """
        {
            "keys": [87, 65, 83, 68, 81, 69]
        }
        """
        self.keys = data['keys']

    def manual_mode(self):
        """
        {}
        """
        self.manual = True
        self.robot.start_open_loop_control()
        return 'OK'

    def auto_mode(self):
        """
        {}
        """
        self.manual = False
        self.robot.stop_open_loop_control()
        return 'OK'

r = Robot()
# add WebHUDMovementSupervisor to working supervisors
r.supervisor().append(WebHUDMovementSupervisor(sio, r))
