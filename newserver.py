import Queue
import socket
import math
from MRobot.FileNameProvider import FileNameProviderByTime
from MRobot.MotorDriver import MD25MotorDriver
from MRobot.MotorHandler import SpeedControllerMotorHandler
from MRobot.MovementController import DifferentialDriveMovementController
from MRobot.MovementSupervisor import FileLoggerMovementSupervisor
from MRobot.OdometryLocalizer import RungeKutta2OdometryLocalizer
from MRobot.RobotLocation import DifferentialDriveRobotLocation
from MRobot.RobotParameters import DifferentialDriveRobotParameters
from MRobot.SpeedController import PIDSpeedController
from MRobot.TrajectoryParameters import DifferentialDriveTrajectoryParameters
from MRobot.TrajectoryPlanner import LinearTrajectoryPlanner, CubicTrajectoryPlanner
from MRobot.TrajectoryTracker import IOLinearizationTrajectoryTracker


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

        @type robot_state: MRobot.RobotState.DifferentialDriveRobotState
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
        robot_parameters = DifferentialDriveRobotParameters(0.05, 0.2995, 360, 0.05, 3.0, 3.0, 1.0, 1.0, 2.0, 127.0,
                                                            -128.0, 0.05)
        self.movement_supervisor = MySupervisor(robot_parameters, FileNameProviderByTime())
        self.linear_trajectory_planner = LinearTrajectoryPlanner()
        self.cubic_trajectory_planner = CubicTrajectoryPlanner()
        odometry_localizer = RungeKutta2OdometryLocalizer(robot_parameters)
        self.localizer = odometry_localizer
        trajectory_tracker = IOLinearizationTrajectoryTracker(robot_parameters.constant_b, robot_parameters.constant_k1,
                                                              robot_parameters.constant_k2, robot_parameters)
        self.tracker = trajectory_tracker
        speed_controller = PIDSpeedController(robot_parameters.constant_kc, robot_parameters.constant_ki,
                                              robot_parameters.constant_kd, robot_parameters.max_value_power,
                                              robot_parameters.min_value_power)
        power_motor_driver = MD25MotorDriver(1, 0x58)
        motor_handler = SpeedControllerMotorHandler(speed_controller, power_motor_driver)
        movement_controller = DifferentialDriveMovementController(self.movement_supervisor,
                                                                  self.linear_trajectory_planner,
                                                                  odometry_localizer,
                                                                  trajectory_tracker, motor_handler, robot_parameters,
                                                                  robot_parameters.sample_time)
        self.motion = movement_controller
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.queue = Queue.Queue()
        self.address = None
        self.index = 0

    def process_path(self, data):
        track_data = data.split(',')

        x_planning = []
        y_planning = []
        z_planning = []

        for i, string in enumerate(track_data[3:]):
            if i % 3 == 0:
                x_planning.append(float(string))
            elif i % 3 == 1:
                y_planning.append(float(string))
            else:
                z_planning.append(float(string))

        locations_tuple = tuple(DifferentialDriveRobotLocation(x_planning[i], y_planning[i], z_planning[i]) for i in
                                range(len(x_planning)))

        trajectory_parameters = DifferentialDriveTrajectoryParameters(locations_tuple, float(track_data[0]),
                                                                      self.motion.sample_time, float(track_data[1]))

        if self.motion.finished:
            self.tracker.smooth_flag = False
            self.motion.trajectory_planner = self.cubic_trajectory_planner
            self.motion.movement_init(trajectory_parameters)
            self.queue.put('path begin')
        else:
            self.queue.put('experiment running')

    def process_reference_points(self, data, points):
        track_data = data.split(',')

        x_planning = []
        y_planning = []
        t_planning = []

        for i, string in enumerate(track_data[1:]):
            if i % 3 == 0:
                x_planning.append(float(string))
            elif i % 3 == 1:
                y_planning.append(float(string))
            else:
                t_planning.append(float(string))

        locations_tuple = tuple(DifferentialDriveRobotLocation(x_planning[i], y_planning[i], 0.) for i in
                                range(len(x_planning)))
        trajectory_parameters = DifferentialDriveTrajectoryParameters(locations_tuple, t_planning[0],
                                                                      self.motion.sample_time)
        if self.motion.ordered_stop:
            self.tracker.smooth_flag = not points
            self.motion.trajectory_planner = self.linear_trajectory_planner
            self.motion.movement_init(trajectory_parameters)
            if points:
                self.queue.put('points begin')
            else:
                self.queue.put('reference begin')
        else:
            self.queue.put('experiment running')

    def process_parameter(self, data):
        parameter, value = data.split(',')
        if parameter == 'constant_kc' or parameter == 'constant_ki' or parameter == 'constant_kd' or \
                        parameter == 'constant_k1' or parameter == 'constant_k2' or parameter == 'constant_b':
            # self.motion.set_parameter(parameter, value)
            self.queue.put('parameter ok')
        else:
            self.queue.put('parameter bad')

    def process_status(self):
        self.queue.put('status %d,%d,%f,%f,%f' % (0, 0, self.motion.robot_state.battery_voltage,
                                                  self.motion.robot_state.current_1, self.motion.robot_state.current2))

    def process_position(self, data):
        if data == 'ask':
            self.queue.put('position %f,%f,%f' % (
                self.localizer.globalLocation.x_position, self.localizer.globalLocation.y_position,
                self.localizer.globalLocation.z_position))
        elif data == 'reset':
            self.localizer.reset_global_location()
            self.queue.put('position %f,%f,%f' % (
                self.localizer.globalLocation.x_position, self.localizer.globalLocation.y_position,
                self.localizer.globalLocation.z_position))
        else:
            position_data = data.split(',')

            x = float(position_data[0])
            y = float(position_data[1])
            t = float(position_data[2])

            delta_x = x - self.localizer.globalLocation.x_position
            delta_y = y - self.localizer.globalLocation.y_position

            beta = math.atan2(delta_y, delta_x)
            theta_n = math.atan2(math.sin(self.localizer.globalLocation.z_position),
                                 math.cos(self.localizer.globalLocation.z_position))
            alpha = beta - theta_n
            l = math.sqrt(delta_x * delta_x + delta_y * delta_y)
            xf_p = l * math.cos(alpha)
            yf_p = l * math.sin(alpha)

            trajectory_parameters = DifferentialDriveTrajectoryParameters((DifferentialDriveRobotLocation(0., 0., 0.),
                                                                           DifferentialDriveRobotLocation(xf_p, yf_p,
                                                                                                          0.)), t,
                                                                          self.motion.sample_time)

            self.tracker.smooth_flag = True
            self.motion.trajectory_planner = self.linear_trajectory_planner
            self.motion.movement_init(trajectory_parameters)

            self.motion.movement_start()

    def process_request(self, request):

        command, data = request.split(' ')

        if command == 'path':
            self.process_path(data)

        elif command == 'points':
            self.process_reference_points(data, True)

        elif command == 'reference':
            self.process_reference_points(data, False)

        elif command == 'experiment' and data == 'stop':
            self.motion.movement_stop()
            self.queue.put('stop ok')

        elif command == 'position':
            self.process_position(data)

        elif command == 'status' and data == 'ask':
            self.process_status()

        elif command == 'parameter':
            self.process_parameter(data)

        elif command == 'localization':
            pass

        elif command == 'movement':
            pass

        else:
            self.queue.put('bad message')

    def sender_thread(self):
        while 1:
            if not self.queue.empty():
                to_send = self.queue.get()
                self.socket.sendto(to_send, self.address)
            if not self.index == self.movement_supervisor.the_index:
                to_send = self.movement_supervisor.the_list[self.index]
                self.socket.sendto(to_send, self.address)
                self.index += 1
                if self.index >= 2000:
                    self.index = 0

    def run(self):
        while 1:
            request, address = self.socket.recvfrom(1024)
            self.address = address
            self.process_request(request)
