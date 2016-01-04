from flask import request, jsonify, json
from WebHUD import app, sio, emit
from WebHUD.utils import allow_origin
from modules.kernel import handler as robot_handler

from threading import Thread
from time import sleep

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
    path = json.loads(path)
    robot_handler.set_path(path)


@app.route('/text', methods=['PUT'])
@allow_origin
def text():
    """
    {
        "text": "some text"
    }
    """
    text = str(request.values['text'])
    # print('In text request')
    # print(' text: %s' % repr(text))
    robot_handler.process_text(text)


@sio.on('manual')  # key press
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


def send_position(x, y, theta):
    #print('emiting pos')
    sio.emit('position', {"x": x, "y": y, 'theta': theta})

def do_nothing(*args, **kwargs):
    pass

# TODO: FIX THIS
# `connect` and `disconnect` event handlers are NOT WORKING

sio.on('connect')
def connect():
    global client_count
    if client_count == 0:
        robot_handler.set_position_notifier(send_position)

    client_count += 1
    print('websocket connected')


sio.on('disconnect')
def disconnect():
    global client_count
    client_count -= 1

    if client_count == 0:
        robot_handler.set_position_notifier(do_nothing)
    print('websocket disconnected')


sio.on('echo')
def echo_reply(data):
    print('client echo:', data)
    emit('echo reply', 'hello at server side')


# TODO: REMOVE THIS
# only when `connect` and `disconnect` are working
robot_handler.set_position_notifier(send_position)
