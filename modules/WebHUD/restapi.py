from flask import request, jsonify, json
from WebHUD import app, sio, emit
from WebHUD.utils import allow_origin
from modules.kernel import handler as robot_handler
from modules.kernel.kernel import link_robot as set_position_notifier

from threading import Thread
from time import sleep

#@sio.on('echo')
#def echo(message):
#    print(message)
#    emit('echo reply', message)


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


count = 0

#@sio.on("send_position_to_client")
#def send_position_to_client():
#
#    emit('position', [1,2,3])
#    print('got into send_position_to_client')
#
#    if count < 20:
#        emit('send_position_to_client')
#        count += 1


#def background_pos():
#    while True:
#        print('test!')
#        sleep(100./1000)
#
#        
#
#        sio.emit('position', )


#@sio.on("get_positions")
#def io_send_position():
#    
#    print('"get_positions" received')
#
#    t = Thread(target=background_pos)
#    t.setDaemon(True)
#    t.start()
#
#    #emit('position', [1,2,3])

#def send_position(x, y, theta):
#    sio.emit('position', {"x": x, "y": y, 'theta': theta})

#set_position_notifier(send_position)
