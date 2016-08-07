import os

from . import app, sio
from .utils import allow_origin
from flask import request, jsonify, json, url_for, send_file
from kernel import handler as robot_handler

from settings import config


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


@sio.on('manual')  # key press
def drive_manual(data):
    """
    {
        "keys": [87, 65, 83, 68, 81, 69]
    }
    """
    keys = data['keys']
    robot_handler.set_keys(keys)


@app.route('/manual_mode', methods=['PUT'])
@allow_origin
def manual_mode():
    """
    {}
    """
    robot_handler.set_mode('manual')
    return 'OK'


@app.route('/auto_mode', methods=['PUT'])
@allow_origin
def auto_mode():
    """
    {}
    """
    robot_handler.set_mode('auto')
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


def send_position(x, y, theta):
    sio.emit('position', {"x": x, "y": y, 'theta': theta})


@sio.on('connect')
def connect():
    global client_count
    if client_count == 0:
        robot_handler.set_position_notifier(send_position)

    client_count += 1


@sio.on('disconnect')
def disconnect():
    global client_count
    client_count -= 1

    if client_count == 0:
        robot_handler.set_position_notifier(None)


@sio.on('echo')
def echo_reply(data):
    print('client echo:', data)
    sio.emit('echo reply', 'hello at server side')
