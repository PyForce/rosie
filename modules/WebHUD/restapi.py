from flask import request, jsonify, json
from WebHUD import app, sio, emit
from WebHUD.utils import allow_origin
from modules.kernel.kernel import link_robot as set_position_notifier


@sio.on('echo', namespace='/test')
def echo(message):
    print(message)
    emit('echo reply', message)


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


@app.route('/metadata', methods=['GET'])
@allow_origin
def metadata():
    """
    {
        "name": "LTL",
        "processor" : "RaspberryPi",
        "motor_controller" : "Arduino Uno",
        "size" : [0.3, 0.5, 0.34],
        "photo": "http://photo_url",
        "sensors": ["seensor1", "sensor2"]
    }
    """
    return jsonify(**json.loads(metadata.__doc__))


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


@app.route('/path', methods=['PUT'])
@allow_origin
def path():
    """
    {
        "path": [(x, y), (x, y), ... ]
    }
    """
    path = request.values['path']
    robot_handler.set_path(path)


@app.route('/text', methods=['PUT'])
@allow_origin
def text():
    """
    {
        "text": "some text"
    }
    """
    text = request.values['text']
    robot_handler.process_text(text)


@sio.on('manual', namespace='/test')  # key press
def drive_manual(data):
    """
    {
        "keys": [87, 65, 83, 68]
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


@app.route('/auto_mode', methods=['PUT'])
@allow_origin
def auto_mode():
    """
    {}
    """
    robot_handler.set_mode('auto')


@app.route('/maps', methods=['PUT'])
@allow_origin
def maps():
    """
    {
        "map": "map_name"
    }
    """
    map = request.values['map']


def send_position(x, y, theta):
    data = {
        "x": x,
        "y": y,
        "theta": theta
    }
    emit(data)


set_position_notifier(send_position)
