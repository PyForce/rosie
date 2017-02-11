import math
import os

from flask import request, jsonify, json, url_for, send_file, abort
from scanner import scanner_server as scanner

from . import app, ws
from .utils import allow_origin
from robot import Robot
from robot.motion.MovementController.Differential import\
    DifferentialDriveRobotLocation
from robot.motion.MovementSupervisor.Differential\
    import DifferentialDriveMovementSupervisor
from robot.motion.TrajectoryPlanner.Differential import\
    DifferentialDriveTrajectoryParameters
from robot.motion.TrajectoryPlanner.Planner.Linear import\
    LinearTrajectoryPlanner
from robot.motion.TrajectoryPlanner.Planner.Cubic import\
    CubicTrajectoryPlanner


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
    x, y, theta = Robot().position()
    return jsonify(x=y, y=-x, theta=theta)


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
    prof = Robot().setting_handler.profile
    return jsonify(prof=prof)


@app.route('/metadata', methods=['GET'])
@allow_origin
def metadata():
    settings = Robot().setting_handler.settings
    data = {
        "name": settings.MOBILE_ROBOT,
        "thumbnail": url_for('.thumbnail'),
        "vector": url_for('.vector'),
        "size": [settings.LARGE, settings.WIDTH, settings.HEIGHT]
    }
    return jsonify(**data)


@app.route('/thumbnail', methods=['GET'])
@allow_origin
def thumbnail():
    profile = Robot().setting_handler.profile
    filePath = os.path.join(os.getcwd(), 'profiles', profile, 'thumbnail.png')
    return send_file(filePath)


@app.route('/vector', methods=['GET'])
@allow_origin
def vector():
    profile = Robot().setting_handler.profile
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


@app.route('/position', methods=['PUT', 'POST'])
@allow_origin
def position():
    """
    {
        "x": x,
        "y": y,
        "theta": theta
    }
    """
    data = request.get_json()
    x = data['x']
    y = data['y']
    theta = data['theta']
    Robot().position(y, -x, theta)
    return 'OK'


@app.route('/path', methods=['PUT', 'POST'])
@allow_origin
def path():
    """
    {
        "path": [(x, y, t), (x, y, t), ... ],
        "smooth": True,
        "interpolation": "cubic",
        "k": 0.1,
        "time": 10,
    }
    """
    values = request.get_json()

    values.setdefault(u'interpolation', 'linear')
    values.setdefault(u'smooth', False)
    values.setdefault(u'k', 0.1)
    values.setdefault(u'time', 10)

    path = values[u'path']

    interpolation = values[u'interpolation']
    if interpolation == u'cubic':
        planner = CubicTrajectoryPlanner()
    elif interpolation == u'linear':
        planner = LinearTrajectoryPlanner()
    else:
        return abort(400)

    r = Robot()

    r.motion.trajectory_tracker.smooth_flag = values[u'smooth']

    if len(path) == 1:
        # convert from web client coordinates
        x, y, t = path[0][1], -path[0][0], values[u'time']

        x0, y0, z0 = r.position()

        delta_x = x - x0
        delta_y = y - y0

        beta = math.atan2(delta_y, delta_x)
        theta_n = math.atan2(math.sin(z0), math.cos(z0))
        alpha = beta - theta_n
        dist = math.sqrt(delta_x * delta_x + delta_y * delta_y)
        xf_p = dist * math.cos(alpha)
        yf_p = dist * math.sin(alpha)

        trajectory_parameters = DifferentialDriveTrajectoryParameters(
            (DifferentialDriveRobotLocation(0., 0., 0.),
             DifferentialDriveRobotLocation(xf_p, yf_p, 0.)),
            t, r.motion.robot_parameters.sample_time)
    else:
        locations_tuple = [DifferentialDriveRobotLocation(
            elem[1], -elem[0], elem[2]) for elem in path]
        trajectory_parameters = DifferentialDriveTrajectoryParameters(
            locations_tuple, values[u'time'], r.motion.sample_time,
            values[u'k'])

    r.change_trajectory_planner(planner)
    r.track(trajectory_parameters)
    return 'OK'


@app.route('/text', methods=['PUT', 'POST'])
@allow_origin
def text():
    """
    {
        "text": "some text"
    }
    """
    text = request.get_json()['text']
    robot_handler.process_text(text)
    return 'OK'


@app.route('/maps')
@allow_origin
def maps():
    """
    {
        "map": "map_name"
    }
    """
    return jsonify([map['name'] for map in Robot().planner.maps()])


@app.route('/map', defaults={'name': ''})
@app.route('/map/<string:name>')
@allow_origin
def map(name):
    """
    {
        "map": "map_name"
    }
    """
    r = Robot()
    if name:
        map = r.planner.get_map(name)
    else:
        map = r.planner.map
    return jsonify(map) if map else abort(404)


@app.route('/clusters')
@allow_origin
def clusters():
    data = {
        cluster.name: [cluster.host, cluster.port]
        for cluster in scanner.clusters
    }
    return jsonify(**data)


class WebHUDMovementSupervisor(DifferentialDriveMovementSupervisor):
    def __init__(self, robot):
        self.robot = robot
        self.keys = []

        self.ws = []

        # register websockets under '/websockets'
        @ws.route('/websocket')
        def websocket(ws):
            self.ws.append(ws)
            message = ws.receive()
            while not ws.closed and message:
                data = json.loads(message)
                if data['type'] == 'keys':
                    self.keys = data['data']
                message = ws.receive()
            # self.ws = None
        # use old-style decorators to subscribe bounded methods
        app.route('/auto_mode', methods=['PUT', 'POST'])(allow_origin(self.auto_mode))
        app.route('/manual_mode', methods=['PUT', 'POST'])(allow_origin(
            self.manual_mode))
        self.last_location = 0, 0, 0

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

        x_, y_, t_ = self.last_location
        if abs(x - x_) + abs(y - y_) + abs(theta - t_) == 0:
            # don't notify when robot not moved
            return

        # TODO: delete this for please!
        for i, websock in enumerate(self.ws):
            if websock.closed:
                self.ws.pop(i)
                continue
            # convert to web client coordinates
            websock.send(json.dumps({'type': 'position',
                                     'data': {'x': -y, 'y': x,
                                              'theta': theta}}))
        # update last location
        self.last_location = x, y, theta

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
r.supervisor().append(WebHUDMovementSupervisor(r))
