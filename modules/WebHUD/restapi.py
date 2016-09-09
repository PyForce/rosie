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
    def __init__(self, sio):
        self.sio = sio
        self.keys = []

    def movement_update(self, state):
        if self.manual:
            # update keys
            pass
        self.sio.emit('position', {'x': state.global_location.x_position,
                                   'y': state.global_location.y_position,
                                   'theta': state.global_location.z_location})

    @sio.on('manual')  # key press
    def drive_manual(self, data):
        """
        {
            "keys": [87, 65, 83, 68, 81, 69]
        }
        """
        self.keys = data['keys']

    @app.route('/manual_mode', methods=['PUT'])
    @allow_origin
    def manual_mode(self):
        """
        {}
        """
        self.manual = True
        return 'OK'

    @app.route('/auto_mode', methods=['PUT'])
    @allow_origin
    def auto_mode(self):
        """
        {}
        """
        self.manual = False
        return 'OK'

r = Robot()
# add WebHUDMovementSupervisor to working supervisors
r.supervisor().append(WebHUDMovementSupervisor(sio))
