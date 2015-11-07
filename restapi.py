from flask import request, make_response, jsonify, json
from WebHUD import app

def allow_origin(f):
    def g(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Access-Control-Allow-Origin']='*'
        return response
    g.__doc__ = f.__doc__
    return g

@allow_origin
@app.route('/odometry', methods=['GET'])
def odometry():
    """
    {
        "x": 2.1,
        "y": 1.3,
        "theta": 3.21
    }
    """
    return jsonify(**json.loads(odometry.__doc__))

@allow_origin
@app.route('/metadata', methods=['GET'])
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
#@allow_origin
def sensor(name):
    """
    {
    }
    """
    return jsonify(**json.loads(sensor.__doc__))


@app.route('/position', methods=['PUT'])
#@allow_origin
def position():
    """
    {
        "x": x,
        "y": y,
        "theta": theta
    }
    """
    x = request.json['x']
    y = request.json['y']
    theta = request.json['theta']

@app.route('/goto', methods=['PUT'])
#@allow_origin
def goto():
    """
    {
        "path": [(x, y), (x, y), ... ]
    }
    """
    path = request.json['path']

@app.route('/text', methods=['PUT'])
#@allow_origin
def text():
    """
    {
        "text": "some text"
    }
    """
    text = request.json['text']

@app.route('/manual_mode', methods=['PUT'])
#@allow_origin
def manual_mode():
    """
    {}
    """
    pass

@app.route('/maps', methods=['PUT'])
#@allow_origin
def maps():
    """
    {
    }
    """
    geojson = request.json

