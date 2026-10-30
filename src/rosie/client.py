"""
rosie client API implementation
"""
import time
import json
import websocket
from threading import Thread
import sys
if sys.version_info[0] == 2:
    import httplib as http_client
else:
    import http.client as http_client


class ClientRobotApi(object):
    """Client http api for rosi."""

    def __init__(self, ip_address='10.0.0.1', port=5000):
        self.ip_address = ip_address
        self.port = port
        self.manual = False
        self.thread_ready = True
        # self.velocity_counter = 0
        self.connection = http_client.HTTPConnection(
            self.ip_address, self.port)
        self.start_ws()
        # self.odometry()
        self.web_xpos, self.web_ypos, self.web_theta = self.odometry()

    def my_http_request(self, method, route, to_send=None, headers={'Content-type': 'application/json'}):
        self.connection.request(method, route, to_send, headers)
        response = self.connection.getresponse()
        return response.read().decode()

    def objetify(self, req):
        """
        Get the json from a request in a unified manner
        """
        # TODO: review why force is required
        return req.get_json(force=True)

    def odometry(self):
        """
        >>> odometry()
        (x,y,theta)
        """
        json_response = self.my_http_request('GET', '/odometry')
        diction = json.loads(json_response)
        self.xpos = diction["x"]
        self.ypos = diction["y"]
        self.theta = diction["theta"]
        return diction["x"], diction["y"], diction["theta"]

    def ultrasonic_measurements(self):
        json_response = self.my_http_request('GET', '/usound')
        diction = json.loads(json_response)
        return diction

    def metadata(self):
        """
        >>>metadata()
        ('SIMUBOT', '/thumbnail', '/vector', False, [0.2, 0.42, 0])
        """

        json_response = self.my_http_request('GET', '/metadata')
        diction = json.loads(json_response)
        return diction["name"], diction["thumbnail"], diction["vector"], diction["video"], diction["size"]

    # def thumbnail(self):
    #     """
    #     ESTA DEVUELVE UNA IMAGEN NO EL FILEPATH DE LA IMAGENDetailed image of the robot
    #     """

    #     json_response = self.my_http_request('GET', '/thumbnail')
    #     diction = json.loads(json_response)
    #     return diction

    # # @app.route('/vector', methods=['GET'])
    # def vector(self):
    #     """
    #     Icon of the robot
    #     """
    #     profile = Robot().setting_handler.profile
    #     filepath = os.path.join(os.getcwd(), 'profiles', profile, 'vector.svg')
    #     return send_file(filepath)

    # # TODO: read a the sensors
    def sensor(self, name):
        """
        >>>sensor(name)
        (13.456738)
        """

        json_response = self.my_http_request('GET', '/sensor/' + name)
        return json_response

    def position(self, x, y, theta):
        """
        Teleports the robot
        >>>position(x,y,theta)
        True
        """

        diction = dict(x=x, y=y, theta=theta)
        json_param = json.dumps(diction)
        self.my_http_request('POST', '/position', json_param)

    def goto(self, x, y, t, planner=False):
        """
        >>>goto(x, y, t, planner=True)
        """
        self.auto_mode()
        diction = dict(target=[x, y, t], planner=planner)
        json_param = json.dumps(diction)
        self.my_http_request('POST', '/goto', json_param)

    def follow(self, path, time):
        """
        >>>follow([[x, y], [x, y], ... ],time)
        True
        """
        self.auto_mode()
        diction = dict(path=path, time=time)
        json_param = json.dumps(diction)
        self.my_http_request('POST', '/follow', json_param)

    def maps(self):
        """
        >>>maps()
        ["Gustavo's House"]
        """
        json_response = self.my_http_request('GET', '/maps')
        map_list = json.loads(json_response)
        return [name for name in map_list]

    # TODO
    def getmap(self, name):
        """
        {
                "map": "map_name"
        }
        """
        json_response = self.my_http_request('GET', '/map/' + name)
        # diction = json.loads(json_response)
        return json_response

    # WEBSOCKETS
    def start_ws(self):
        # print(url_rule)
        a_thread = Thread(target=self.ws_receive)
        a_thread.start()

    def ws_receive(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("ws://%s:%s/%s" % (self.ip_address, self.port, "websocket"), on_open=None,
                                         on_message=self.ws_message,
                                         on_error=self.ws_error,
                                         on_close=self.close_ws)
        self.ws.run_forever()

    def ws_message(self, ws, message):
        message = json.loads(message)
        if message["type"] == "position":
            self.web_xpos = (message["data"]["x"])
            # print (self.web_xpos)
            self.web_ypos = (message["data"]["y"])
            self.web_theta = (message["data"]["theta"])

    def ws_error(self, ws, error):
        # print (error)
        pass

    def close_ws(self, ws):
        print ("### closed ###")

    # auto_mode and manual_mode are not putting OPTIONS on the server, unlike
    # the web app clicking way
    def auto_mode(self):
        self.manual = False
        self.my_http_request('POST', '/auto_mode')

    def manual_mode(self):
        self.manual = True
        self.my_http_request('POST', '/manual_mode')

    def velocity_vector(self, vector):
        diction = dict(data=vector, type="move")
        json_param = json.dumps(diction)
        self.ws.send(json_param)

    def direction(self, vector, moving_time=5):
        self.thread_ready = False
        self.manual_mode()
        # print '\n\nTHIS IS COUNTER: ', self.velocity_counter, '\n\n'
        # self.velocity_counter += 1
        self.velocity_vector(vector)
        time.sleep(moving_time)
        self.velocity_vector([0, 0, 0])
        self.thread_ready = True
        # print self.odometry()

    def start_direction(self, vector, moving_time=1):
        if self.thread_ready:
            direction_thread = Thread(
                target=self.direction, args=(vector, moving_time))
            direction_thread.start()
        else:
            pass

if __name__ == '__main__':
    # a_robot = ClientRobotApi('127.0.0.1', 5000)
    # a_robot = ClientRobotApi('192.168.1.146', 5000)
    a_robot = ClientRobotApi('10.42.0.216', 5000)
    a_robot.velocity_vector([0, 0, 0])
    # a_robot.start_direction([0, 0, .4], 1)
    # print (a_robot.odometry())
    # a_robot.position(0, 0, 0)
    # a_robot.start_direction([0, 0, 0.2], 1.2)
    # a_robot.start_direction([0, -0.2, 0], 0.2)
    # odometry = a_robot.odometry()
    # print odometry
    # print '\n\nThis is odometry magnitude', (odometry[0]**2 + odometry[1]**2)**0.5
    # a_robot.start_direction(
    #     [0.3, 0.3, 0], 20)

    # print "\n\n#################### Switching to auto_mode.
    # ####################\n\n"
    # a_robot.goto(0, 0.1, 5, planner=False)
    # a_robot.follow([[1, 1], [1.2, 1.4],[1.4, 1.6],[1.6, 1.8],[1.8, 2.0],[2.0, 2.2] ],5)

    # print (a_robot.xpos)
    # time.sleep(2)
    # print (a_robot.xpos)
    # time.sleep(2)
    # print (a_robot.xpos)

    # a_robot.goto(10, 10, 20, planner=False)
    # (a_robot.position(0, 2, 6))
    # print (a_robot.maps())
    # print (a_robot.getmap("Gustavo's House"))
