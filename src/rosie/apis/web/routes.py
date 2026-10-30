"""
rosie API implementation
"""
import asyncio
import json
import logging
import os

from fastapi import (APIRouter, Depends, HTTPException, Request, WebSocket,
                     WebSocketDisconnect)
from fastapi.responses import FileResponse, JSONResponse, Response

from rosie.robot import PROFILES_DIR, Robot
from rosie.motion.supervisor \
    import DifferentialDriveMovementSupervisor


router = APIRouter()


def get_robot(request: Request) -> Robot:
    """
    The robot this API serves
    """
    return request.app.state.robot


async def objetify(req):
    """
    Get the json from a request in a unified manner
    """
    # parsed whatever the content type, as clients don't always set it
    return json.loads(await req.body())


@router.get('/odometry')
def odometry(robot: Robot = Depends(get_robot)):
    """
    {
        "x": 2.1,
        "y": 1.3,
        "theta": 3.21
    }
    """
    xpos, ypos, theta = robot.position()
    return {"x": xpos, "y": ypos, "theta": theta}


@router.get('/metadata')
def metadata(request: Request, robot: Robot = Depends(get_robot)):
    """
    {
        "name": 'SIMUBOT',
        "thumbnail": '/thumbnail',
        "vector": '/vector',
        "video": ':8000/video'
        "size": [0.4, 0.2, 0.2]
    }
    """
    handler = robot.setting_handler

    videouri = False
    if hasattr(handler.settings, 'VIDEO_URI'):
        videouri = handler.settings.VIDEO_URI

    return {
        "name": handler.settings.MOBILE_ROBOT,
        "thumbnail": request.app.url_path_for('thumbnail'),
        "vector": request.app.url_path_for('vector'),
        "video": videouri,
        "size": [handler.settings.LARGE, handler.settings.WIDTH,
                 handler.settings.HEIGHT],
        "profile": handler.profile
    }


@router.get('/thumbnail')
def thumbnail(robot: Robot = Depends(get_robot)):
    """
    Detailed image of the robot
    """
    profile = robot.setting_handler.profile
    filepath = os.path.join(PROFILES_DIR, profile, 'thumbnail.png')
    return FileResponse(filepath)


@router.get('/vector')
def vector(robot: Robot = Depends(get_robot)):
    """
    Icon of the robot
    """
    profile = robot.setting_handler.profile
    filepath = os.path.join(PROFILES_DIR, profile, 'vector.svg')
    return FileResponse(filepath)


# TODO: read a the sensors
# @router.get('/sensor/{name}')
# def sensor(name):
#     """
#     {
#         "sensor_name": sensor_reading
#     }
#     """
#     return json.loads(sensor.__doc__ % name)


@router.post('/position')
async def position(request: Request, robot: Robot = Depends(get_robot)):
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
    robot.position(xpos, ypos, theta)
    return Response()


@router.post('/goto')
async def goto(request: Request, robot: Robot = Depends(get_robot)):
    """
    {
        "target": [x, y, t],
        "planner": false
    }
    """
    values = await objetify(request)
    xpos, ypos, theta = values['target']
    planner = values.get('planner', False)

    if planner:
        try:
            robot.go_to_with_planner(*values['target'])
        except Exception as ex:
            return JSONResponse({'error': ex.message}, status_code=409)  # CONFLICT
    else:
        robot.go_to(xpos, ypos, theta)

    return Response()


@router.post('/follow')
async def follow(request: Request, robot: Robot = Depends(get_robot)):
    """
    {
        "path": [[x, y], [x, y], ... ],
        "time": t
    }
    """
    values = await objetify(request)

    robot.follow(values['path'], values['time'])
    return Response()


@router.get('/maps')
def maps(robot: Robot = Depends(get_robot)):
    """
    [
        "map_name", ...
    ]
    """
    return {"maps": [name for name in robot.maps()]}


@router.get('/map')
@router.get('/map/{name}')
def getmap(name: str = '', robot: Robot = Depends(get_robot)):
    """
    {
        "map": "map_name"
    }
    """
    worldmap = robot.get_map(name)
    if not worldmap:
        raise HTTPException(status_code=404)
    return worldmap


class RestAPIMovementSupervisor(DifferentialDriveMovementSupervisor):
    """
    Supervisor to send movement updates to rosie web clients
    """

    def __init__(self, robot):
        super(RestAPIMovementSupervisor, self).__init__()
        self.robot = robot
        self.manual = False

        self.clients = []
        # pending sends, kept until done (the event loop only keeps weak ones)
        self.sending = set()

        self.last_location = 0, 0, 0

    async def websocket(self, websocket: WebSocket):
        """
        Web client communication API
        """
        await websocket.accept()
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
            task = asyncio.create_task(websock.send_text(message))
            self.sending.add(task)
            task.add_done_callback(self.sent)
        # update last location
        self.last_location = move_x, move_y, move_theta

    def sent(self, task):
        """
        Forget a finished send; a client gone meanwhile is not an error
        """
        self.sending.discard(task)
        if not task.cancelled():
            task.exception()

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

