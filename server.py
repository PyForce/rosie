import Queue
import socket
import math
from robot import Robot

from robot.motion.MovementController.Differential import DifferentialDriveRobotLocation
from robot.motion.MovementSupervisor.Supervisor.FileLogger import FileLoggerMovementSupervisor
from robot.motion.TrajectoryPlanner.Differential import DifferentialDriveTrajectoryParameters
from robot.motion.TrajectoryPlanner.Planner.Cubic import CubicTrajectoryPlanner
from robot.motion.TrajectoryPlanner.Planner.Linear import LinearTrajectoryPlanner
from tools.FileNameProvider import FileNameProviderByTime


class MySupervisor(FileLoggerMovementSupervisor):
    def __init__(self, robot_parameters, file_name_provider):
        super(MySupervisor, self).__init__(robot_parameters, file_name_provider)
        self.the_list = range(2000)
        self.the_index = 0

    def to_list(self, m):
        self.the_list[self.the_index] = m
        self.the_index += 1
        if self.the_index >= 2000:
            self.the_index = 0

    def movement_update(self, robot_state):
        """

        @type robot_state: motion.RobotState.DifferentialDriveRobotState
        """
        super(MySupervisor, self).movement_update(robot_state)
        self.to_list('position %f,%f,%f' % (
            robot_state.global_location.x_position, robot_state.global_location.y_position,
            robot_state.global_location.z_position))

    def movement_end(self):
        super(MySupervisor, self).movement_end()
        self.to_list('experiment done')


class newServer:
    def __init__(self, port):
        self.r = Robot()
        self.r.change_supervisor(MySupervisor(self.r.motion.robot_parameters, FileNameProviderByTime()))
        

        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.queue = Queue.Queue()
        self.address = None
        self.index = 0

    def _extractXYTPlanning(self, track_data, index):
        x_planning = []
        y_planning = []
        t_planning = []

        
        for i, string in enumerate(track_data[index:]):
            if i % 3 == 0:
                x_planning.append(float(string))
            elif i % 3 == 1:
                y_planning.append(float(string))
            else:
                t_planning.append(float(string))

        return x_planning, y_planning, t_planning



    def process_path(self, data):
        track_data = data.split(',')
        x_planning, y_planning, t_planning = self._extractXYTPlanning(track_data, 3)

        locations_tuple = tuple(DifferentialDriveRobotLocation(x_planning[i], y_planning[i], t_planning[i]) for i in
                                range(len(x_planning)))

        trajectory_parameters = DifferentialDriveTrajectoryParameters(locations_tuple, float(track_data[0]),
                                                                      self.r.motion.sample_time, float(track_data[1]))

        if self.r.motion.ordered_stop:
            self.r.motion.trajectory_tracker.smooth_flag = False
            cubic_trajectory_planner = CubicTrajectoryPlanner()           
            self.r.change_trajectory_planner(cubic_trajectory_planner)
            self.r.track(trajectory_parameters)
            self.queue.put('path begin')
        else:
            self.queue.put('experiment running')

    def process_reference_points(self, data, points):
        track_data = data.split(',')
        x_planning, y_planning, t_planning = self._extractXYTPlanning(track_data, 1)

        locations_tuple = tuple(DifferentialDriveRobotLocation(x_planning[i], y_planning[i], 0.) for i in
                                range(len(x_planning)))
        trajectory_parameters = DifferentialDriveTrajectoryParameters(locations_tuple, t_planning[1],
                                                                      self.r.motion.sample_time)
        if self.r.motion.ordered_stop:
            self.r.motion.trajectory_tracker.smooth_flag = not points

            lineal_trajectory_planner = LinearTrajectoryPlanner()           
            self.r.change_trajectory_planner(lineal_trajectory_planner)
            self.r.track(trajectory_parameters)

            if points:
                self.queue.put('points begin')
            else:
                self.queue.put('reference begin')
        else:
            self.queue.put('experiment running')

    def process_parameter(self, data):
        # TODO: Fix This
        parameter, value = data.split(',')
        if parameter == 'constant_kc' or parameter == 'constant_ki' or parameter == 'constant_kd' or \
                        parameter == 'constant_k1' or parameter == 'constant_k2' or parameter == 'constant_b':
            # self.r.motion.set_parameter(parameter, value)
            self.queue.put('parameter ok')
        else:
            self.queue.put('parameter bad')

    def process_status(self):
        self.queue.put('status %d,%d,%f,%f,%f' % (0, 0, self.r.motion.robot_state.battery_voltage,
                                                  self.r.motion.robot_state.current_1, self.r.motion.robot_state.current2))

    def process_position(self, data):
        current_position = self.r.position()
        if data == 'ask':
            self.queue.put('position %f,%f,%f' % current_position)
        elif data == 'reset':
            self.r.motion.odometry_localizer.reset_global_location()
            self.queue.put('position %f,%f,%f' % current_position)
        else:
            position_data = data.split(',')

            x, y, t = float(position_data[0]), float(position_data[1]), float(position_data[2])

            x0, y0, z0 = current_position

            delta_x = x - x0
            delta_y = y - y0

            beta = math.atan2(delta_y, delta_x)
            theta_n = math.atan2(math.sin(z0), math.cos(z0))
            alpha = beta - theta_n
            l = math.sqrt(delta_x * delta_x + delta_y * delta_y)
            xf_p = l * math.cos(alpha)
            yf_p = l * math.sin(alpha)

            trajectory_parameters = DifferentialDriveTrajectoryParameters((DifferentialDriveRobotLocation(0., 0., 0.),
                                                                            DifferentialDriveRobotLocation(xf_p, yf_p,0.)), 
                                                                            t, self.r.motion.robot_parameters.sample_time)

            self.r.motion.trajectory_tracker.smooth_flag = True
            lineal_trajectory_planner = LinearTrajectoryPlanner()           
            self.r.change_trajectory_planner(lineal_trajectory_planner)
            self.r.track(trajectory_parameters)

    def process_request(self, request):

        command, data = request.split(' ')

        if command == 'path':
            self.process_path(data)

        elif command == 'points':
            self.process_reference_points(data, True)

        elif command == 'reference':
            self.process_reference_points(data, False)

        elif command == 'experiment' and data == 'stop':
            self.r.motion.movement_stop()
            self.queue.put('stop ok')

        elif command == 'position':
            self.process_position(data)

        elif command == 'status' and data == 'ask':
            self.process_status()

        elif command == 'parameter':
            self.process_parameter(data)

        else:
            self.queue.put('bad message')

    def sender_thread(self):
        while 1:
            if not self.queue.empty():
                to_send = self.queue.get()
                self.socket.sendto(to_send, self.address)
            if not self.index == self.r.motion.movement_supervisor.the_index:
                to_send = self.r.motion.movement_supervisor.the_list[self.index]
                self.socket.sendto(to_send, self.address)
                self.index += 1
                if self.index >= 2000:
                    self.index = 0

    def run(self):
        while 1:
            request, address = self.socket.recvfrom(1024)
            self.address = address
            self.process_request(request)
