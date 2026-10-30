"""
rosie API implementation
"""
import asyncio
import json
import logging
import os

from fastapi import HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, Response

from . import app
from robot import Robot
from robot.motion.MovementSupervisor.Differential \
    import DifferentialDriveMovementSupervisor


async def objetify(req):
    """
    Get the json from a request in a unified manner
    """
    # parsed whatever the content type, as clients don't always set it
    return json.loads(await req.body())


@app.get('/odometry')
def odometry():
    """
    {
        "x": 2.1,
        "y": 1.3,
        "theta": 3.21
    }
    """
    xpos, ypos, theta = Robot().position()
    return {"x": xpos, "y": ypos, "theta": theta}


@app.get('/metadata')
def metadata():
    """
    {
        "name": 'SIMUBOT',
        "thumbnail": '/thumbnail',
        "vector": '/vector',
        "video": ':8000/video'
        "size": [0.4, 0.2, 0.2]
    }
    """
    handler = Robot().setting_handler

    videouri = False
    if hasattr(handler.settings, 'VIDEO_URI'):
        videouri = handler.settings.VIDEO_URI

    return {
        "name": handler.settings.MOBILE_ROBOT,
        "thumbnail": app.url_path_for('thumbnail'),
        "vector": app.url_path_for('vector'),
        "video": videouri,
        "size": [handler.settings.LARGE, handler.settings.WIDTH,
                 handler.settings.HEIGHT],
        "profile": handler.profile
    }


@app.get('/thumbnail')
def thumbnail():
    """
    Detailed image of the robot
    """
    profile = Robot().setting_handler.profile
    filepath = os.path.join(os.getcwd(), 'profiles', profile, 'thumbnail.png')
    return FileResponse(filepath)


@app.get('/vector')
def vector():
    """
    Icon of the robot
    """
    profile = Robot().setting_handler.profile
    filepath = os.path.join(os.getcwd(), 'profiles', profile, 'vector.svg')
    return FileResponse(filepath)


# TODO: read a the sensors
# @app.get('/sensor/{name}')
# def sensor(name):
#     """
#     {
#         "sensor_name": sensor_reading
#     }
#     """
#     return json.loads(sensor.__doc__ % name)


@app.post('/position')
async def position(request: Request):
    """
    Teleports the robot
    {
        "x": x,
        "y": y,
        "theta": theta
    }
    """
    data = await objetify(request)
    xpos = data['x']
    ypos = data['y']
    theta = data['theta']
    Robot().position(xpos, ypos, theta)
    return Response()


@app.post('/goto')
async def goto(request: Request):
    """
    {
        "target": [x, y, t],
        "planner": false
    }
    """
    values = await objetify(request)
    xpos, ypos, theta = values['target']
    planner = values.get('planner', False)

    robot = Robot()
    if planner:
        try:
            robot.go_to_with_planner(*values['target'])
        except Exception as ex:
            return JSONResponse({'error': ex.message}, status_code=409)  # CONFLICT
    else:
        robot.go_to(xpos, ypos, theta)

    return Response()


@app.post('/follow')
async def follow(request: Request):
    """
    {
        "path": [[x, y], [x, y], ... ],
        "time": t
    }
    """
    values = await objetify(request)

    robot = Robot()
    robot.follow(values['path'], values['time'])
    return Response()


@app.get('/maps')
def maps():
    """
    [
        "map_name", ...
    ]
    """
    return {"maps": [name for name in Robot().maps()]}


@app.get('/map')
@app.get('/map/{name}')
def getmap(name: str = ''):
    """
    {
        "map": "map_name"
    }
    """
    robot = Robot()
    worldmap = robot.get_map(name)
    if not worldmap:
        raise HTTPException(status_code=404)
    return worldmap


class RestAPIMovementSupervisor(DifferentialDriveMovementSupervisor):
    """
    Supervisor to send movement updates to rosie web clients
    """

    def __init__(self):
        super(RestAPIMovementSupervisor, self).__init__()
        self.robot = Robot()
        self.manual = False

        self.clients = []
        # the server's event loop, known once a client connects; movement
        # updates come from the motion timer, outside of it
        self.loop = None

        # register websockets under '/websocket'
        app.add_api_websocket_route('/websocket', self.websocket)

        # bound methods can't use the decorators
        app.add_api_route('/auto_mode', self.auto_mode, methods=['PUT', 'POST'])
        app.add_api_route('/manual_mode', self.manual_mode,
                          methods=['PUT', 'POST'])

        self.last_location = 0, 0, 0

    async def websocket(self, websocket: WebSocket):
        """
        Web client communication API
        """
        await websocket.accept()
        self.loop = asyncio.get_running_loop()
        logging.debug("connected websocket client: %s", websocket.client)
        self.clients.append(websocket)
        try:
            while True:
                data = json.loads(await websocket.receive_text())
                if data['type'] == 'move' and self.manual:
                    self.robot.add_movement(data['data'])
        except WebSocketDisconnect:
            pass
        finally:
            self.clients.remove(websocket)

    def movement_begin(self, *args, **kwargs):
        pass

    def movement_end(self, *args, **kwargs):
        pass

    def movement_update(self, state):
        move_x, move_y, move_theta = state.global_location.x_position,\
            state.global_location.y_position, state.global_location.z_position

        prev_x, prev_y, prev_theta = self.last_location
        if abs(move_x - prev_x) + abs(move_y - prev_y) + abs(move_theta -
                                                             prev_theta) == 0:
            # don't notify when robot not moved
            return

        message = json.dumps({'type': 'position',
                              'data': {'x': move_x, 'y': move_y,
                                       'theta': move_theta}})
        for websock in list(self.clients):
            asyncio.run_coroutine_threadsafe(websock.send_text(message),
                                             self.loop)
        # update last location
        self.last_location = move_x, move_y, move_theta

    def manual_mode(self):
        """
        {}
        """
        self.manual = True
        self.robot.start_open_loop_control()
        return Response()

    def auto_mode(self):
        """
        {}
        """
        self.manual = False
        self.robot.stop_open_loop_control()
        return Response()


# add RestAPIMovementSupervisor to working supervisors
Robot().supervisor().append(RestAPIMovementSupervisor())
