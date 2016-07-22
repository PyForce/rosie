from abc import ABCMeta, abstractmethod

__author__ = 'Silvio'


class DifferentialDriveMovementSupervisor:
    """
    Abstract class to supervise a differential drive mobile robot in a movement
    
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def movement_begin(self, expected_updates):
        """
        Method to be called when the movement begins

        @param expected_updates: Number of times movement_updates wil be called
        @type expected_updates: int
        """
        pass

    @abstractmethod
    def movement_update(self, robot_state):
        """
        Method to be called when the state of the robot changes during the movement
        
        @type robot_state: MRobot.RobotState.DifferentialDriveRobotState
        @param robot_state: the new state of the robot
        """
        pass

    @abstractmethod
    def movement_end(self):
        """
        Method to be called when the movement ends

        """
        pass


class FileLoggerMovementSupervisor(DifferentialDriveMovementSupervisor):
    """
    Class to supervise a differential drive mobile robot in a movement using a .m file

    @param robot_parameters: Parameters of the robot
    @param file_name_provider: The name provider used to create the files
    @type robot_parameters: MRobot.RobotParameters.DifferentialDriveRobotParameters
    @type file_name_provider: MRobot.FileNameProvider.FileNameProvider
    """

    def __init__(self, robot_parameters, file_name_provider):
        super(FileLoggerMovementSupervisor, self).__init__()
        self.robot_parameters = robot_parameters
        self.file_name_provider = file_name_provider
        self.time_vector = list()
        self.sample_time_vector = list()
        self.x_position_vector = list()
        self.x_speed_vector = list()
        self.y_position_vector = list()
        self.y_speed_vector = list()
        self.z_position_vector = list()
        self.z_speed_vector = list()

        self.x_ref_vector = list()
        self.x_ref_speed_vector = list()
        self.y_ref_vector = list()
        self.y_ref_speed_vector = list()
        self.z_ref_vector = list()
        self.z_ref_speed_vector = list()

        self.speed_x_ref_vector = list()
        self.speed_y_ref_vector = list()
        self.angular_speed_1_vector = list()
        self.current_1_vector = list()
        self.angular_1_ref_vector = list()
        self.angular_speed_2_vector = list()
        self.current_2_vector = list()
        self.angular_2_ref_vector = list()
        self.updates_done = 0

    def movement_begin(self, expected_updates):
        """
        Method to be called when the movement begins

        @param expected_updates: Number of times movement_updates wil be called
        @type expected_updates: int
        """
        self.updates_done = 0
        self.time_vector = range(expected_updates)
        self.sample_time_vector = range(expected_updates)
        self.x_position_vector = range(expected_updates)
        self.x_speed_vector = range(expected_updates)
        self.y_position_vector = range(expected_updates)
        self.y_speed_vector = range(expected_updates)
        self.z_position_vector = range(expected_updates)
        self.z_speed_vector = range(expected_updates)

        self.x_ref_vector = range(expected_updates)
        self.x_ref_speed_vector = range(expected_updates)
        self.y_ref_vector = range(expected_updates)
        self.y_ref_speed_vector = range(expected_updates)
        self.z_ref_vector = range(expected_updates)
        self.z_ref_speed_vector = range(expected_updates)

        self.speed_x_ref_vector = range(expected_updates)
        self.speed_y_ref_vector = range(expected_updates)
        self.angular_speed_1_vector = range(expected_updates)
        self.current_1_vector = range(expected_updates)
        self.angular_1_ref_vector = range(expected_updates)
        self.angular_speed_2_vector = range(expected_updates)
        self.current_2_vector = range(expected_updates)
        self.angular_2_ref_vector = range(expected_updates)

    def movement_update(self, robot_state):
        """
        Method to be called when the state of the robot changes during the movement

        @type robot_state: MRobot.RobotState.DifferentialDriveRobotState
        @param robot_state: the new state of the robot
        """
        if self.updates_done >= len(self.x_position_vector):
            return

        self.sample_time_vector[self.updates_done] = robot_state.elapsed_time

        self.x_position_vector[self.updates_done] = robot_state.location.x_position
        self.y_position_vector[self.updates_done] = robot_state.location.y_position
        self.z_position_vector[self.updates_done] = robot_state.location.z_position

        self.x_ref_vector[self.updates_done] = robot_state.reference_location.x_position
        self.y_ref_vector[self.updates_done] = robot_state.reference_location.y_position
        self.z_ref_vector[self.updates_done] = robot_state.reference_location.z_position

        self.x_ref_speed_vector[self.updates_done] = robot_state.reference_speed.x_speed
        self.y_ref_speed_vector[self.updates_done] = robot_state.reference_speed.y_speed
        self.z_ref_speed_vector[self.updates_done] = robot_state.reference_speed.z_speed

        self.speed_x_ref_vector[self.updates_done] = robot_state.x_speed_ref
        self.speed_y_ref_vector[self.updates_done] = robot_state.y_speed_ref

        self.angular_speed_1_vector[self.updates_done] = robot_state.angular_speed_1
        self.angular_1_ref_vector[self.updates_done] = robot_state.angular_ref_1
        self.current_1_vector[self.updates_done] = robot_state.current_1

        self.angular_speed_2_vector[self.updates_done] = robot_state.angular_speed_2
        self.angular_2_ref_vector[self.updates_done] = robot_state.angular_ref_2
        self.current_2_vector[self.updates_done] = robot_state.current_2

        self.updates_done += 1

    def movement_end(self):
        """
        Method to be called when the movement ends

        """
        self.time_vector[0] = 0.
        for i in range(self.updates_done - 1):
            self.time_vector[i + 1] = self.time_vector[i] + self.sample_time_vector[i]
            self.x_speed_vector[i] = (self.x_position_vector[i + 1] - self.x_position_vector[i]) / \
                                     (self.sample_time_vector[i])
            self.y_speed_vector[i] = (self.y_position_vector[i + 1] - self.y_position_vector[i]) / \
                                     (self.sample_time_vector[i])
            self.z_speed_vector[i] = (self.z_position_vector[i + 1] - self.z_position_vector[i]) / \
                                     (self.sample_time_vector[i])

        self.x_speed_vector[self.updates_done - 1] = self.x_speed_vector[self.updates_done - 2]
        self.y_speed_vector[self.updates_done - 1] = self.y_speed_vector[self.updates_done - 2]
        self.z_speed_vector[self.updates_done - 1] = self.z_speed_vector[self.updates_done - 2]

        save_file = open(self.file_name_provider.get_file_name() + ".m", 'w')

        save_file.write("close all;\r\n")
        save_file.write("clear all;\r\n")
        save_file.write("clc;\r\n\r\n")

        save_file.write("count=%f;\r\n" % self.updates_done)
        save_file.write("radius=%f;\r\n" % self.robot_parameters.wheel_radius)
        save_file.write("distance=%f;\r\n" % self.robot_parameters.wheel_distance)
        save_file.write("constant_b=%f;\r\n" % self.robot_parameters.constant_b)
        save_file.write("constant_k1=%f;\r\n" % self.robot_parameters.constant_k1)
        save_file.write("constant_k2=%f;\r\n" % self.robot_parameters.constant_k2)
        save_file.write("constant_ki=%f;\r\n" % self.robot_parameters.constant_ki)
        save_file.write("constant_kd=%f;\r\n" % self.robot_parameters.constant_kd)
        save_file.write("constant_kc=%f;\r\n" % self.robot_parameters.constant_kc)

        for i in range(self.updates_done):
            save_file.write("speed1(%d) = %f ;\r\n" % (i + 1, self.angular_speed_1_vector[i]))
            save_file.write("speed2(%d) = %f ;\r\n" % (i + 1, self.angular_speed_2_vector[i]))
            save_file.write("current1(%d) = %f ;\r\n" % (i + 1, self.current_1_vector[i]))
            save_file.write("current2(%d) = %f ;\r\n" % (i + 1, self.current_2_vector[i]))
            save_file.write("time(%d) = %f ;\r\n" % (i + 1, self.time_vector[i]))
            save_file.write("sample_time(%d) = %f ;\r\n" % (i + 1, self.sample_time_vector[i]))
            save_file.write("ref1(%d) = %f ;\r\n" % (i + 1, self.angular_1_ref_vector[i]))
            save_file.write("ref2(%d) = %f ;\r\n" % (i + 1, self.angular_2_ref_vector[i]))
            save_file.write("x(%d) = %f ;\r\n" % (i + 1, self.x_position_vector[i]))
            save_file.write("y(%d) = %f ;\r\n" % (i + 1, self.y_position_vector[i]))
            save_file.write("z(%d) = %f ;\r\n" % (i + 1, self.z_position_vector[i]))
            save_file.write("xd(%d) = %f ;\r\n" % (i + 1, self.x_ref_vector[i]))
            save_file.write("yd(%d) = %f ;\r\n" % (i + 1, self.y_ref_vector[i]))
            save_file.write("zd(%d) = %f ;\r\n" % (i + 1, self.z_ref_vector[i]))
            save_file.write("dx(%d) = %f ;\r\n" % (i + 1, self.x_speed_vector[i]))
            save_file.write("dy(%d) = %f ;\r\n" % (i + 1, self.y_speed_vector[i]))
            save_file.write("dz(%d) = %f ;\r\n" % (i + 1, self.z_speed_vector[i]))
            save_file.write("dxd(%d) = %f ;\r\n" % (i + 1, self.x_ref_speed_vector[i]))
            save_file.write("dyd(%d) = %f ;\r\n" % (i + 1, self.y_ref_speed_vector[i]))
            save_file.write("dzd(%d) = %f ;\r\n" % (i + 1, self.z_ref_speed_vector[i]))
            save_file.write("dxr(%d) = %f ;\r\n" % (i + 1, self.speed_x_ref_vector[i]))
            save_file.write("dyr(%d) = %f ;\r\n" % (i + 1, self.speed_y_ref_vector[i]))

        save_file.write("\r\nfigure;\r\n")
        save_file.write("plot(time,x,time,xd) ;\r\n")
        save_file.write("title(\'X Position vs Time.\') ;\r\n")
        save_file.write("legend(\'X\',\'X - Reference\') ;\r\n")
        save_file.write("xlabel(\'Time (s)') ;\r\n")
        save_file.write("ylabel(\'X Position (m)') ;\r\n")
        save_file.write("grid on\r\n")

        save_file.write("\r\nfigure;\r\n")
        save_file.write("plot(time,y,time,yd) ;\r\n")
        save_file.write("title(\'Y Position vs Time.\') ;\r\n")
        save_file.write("legend(\'Y\',\'Y - Reference\') ;\r\n")
        save_file.write("xlabel(\'Time (s)') ;\r\n")
        save_file.write("ylabel(\'Y Position (m)') ;\r\n")
        save_file.write("grid on\r\n")

        save_file.write("\r\nfigure;\r\n")
        save_file.write("plot(time,z,time,zd) ;\r\n")
        save_file.write("title(\'Orientation vs Time.\') ;\r\n")
        save_file.write("legend(\'Z\',\'Z - Reference\') ;\r\n")
        save_file.write("xlabel(\'Time (s)') ;\r\n")
        save_file.write("ylabel(\'Z Position (rad)') ;\r\n")
        save_file.write("grid on\r\n")

        save_file.write("\r\nfigure;\r\n")
        save_file.write("plot(x,y,xd,yd) ;\r\n")
        save_file.write("title(\'Y Position vs X Position (Path).\') ;\r\n")
        save_file.write("legend(\'Path\',\'Path - Reference\') ;\r\n")
        save_file.write("xlabel(\'X Position (m)') ;\r\n")
        save_file.write("ylabel(\'Y Position (m)') ;\r\n")
        save_file.write("grid on\r\n")

        save_file.write("\r\nfigure;\r\n")
        save_file.write("plot(time,speed1,time,ref1) ;\r\n")
        save_file.write("title(\'WL vs Time.\') ;\r\n")
        save_file.write("legend(\'WL\',\'WL - Reference\') ;\r\n")
        save_file.write("xlabel(\'Time (s)') ;\r\n")
        save_file.write("ylabel(\'Angular Speed (rad/s)') ;\r\n")
        save_file.write("grid on\r\n")

        save_file.write("\r\nfigure;\r\n")
        save_file.write("plot(time,speed2,time,ref2) ;\r\n")
        save_file.write("title(\'WR vs Time.\') ;\r\n")
        save_file.write("legend(\'WR\',\'WR - Reference\') ;\r\n")
        save_file.write("xlabel(\'Time (s)') ;\r\n")
        save_file.write("ylabel(\'Angular Speed (rad/s)') ;\r\n")
        save_file.write("grid on\r\n")

        save_file.write("\r\nfigure;\r\n")
        save_file.write("plot(time,current1,time,current2) ;\r\n")
        save_file.write("title(\'Currents vs Time.\') ;\r\n")
        save_file.write("legend(\'Left Motor\',\'Right Motor\') ;\r\n")
        save_file.write("xlabel(\'Time (s)') ;\r\n")
        save_file.write("ylabel(\'Current (A)') ;\r\n")
        save_file.write("grid on\r\n")

        save_file.write("\r\nfigure;\r\n")
        save_file.write("plot(time,dx,time,dxr,time,dxd) ;\r\n")
        save_file.write("title(\'X Speed vs Time.\') ;\r\n")
        save_file.write("legend(\'DX\',\'DXR - Reference\',\'DXD - Planning\') ;\r\n")
        save_file.write("xlabel(\'Time (s)') ;\r\n")
        save_file.write("ylabel(\'X Speed (m/s)') ;\r\n")
        save_file.write("grid on\r\n")

        save_file.write("\r\nfigure;\r\n")
        save_file.write("plot(time,dy,time,dyr,time,dyd) ;\r\n")
        save_file.write("title(\'Y Speed vs Time.\') ;\r\n")
        save_file.write("legend(\'DY\',\'DYR - Reference\',\'DYD - Planning\') ;\r\n")
        save_file.write("xlabel(\'Time (s)') ;\r\n")
        save_file.write("ylabel(\'Y Speed (m/s)') ;\r\n")
        save_file.write("grid on\r\n")

        save_file.write("\r\nfigure;\r\n")
        save_file.write("plot(time,dz,time,dzd) ;\r\n")
        save_file.write("title(\'Z Speed vs Time.\') ;\r\n")
        save_file.write("legend(\'DZ\',\'DZD - Planning\') ;\r\n")
        save_file.write("xlabel(\'Time (s)') ;\r\n")
        save_file.write("ylabel(\'Z Speed (rad/s)') ;\r\n")
        save_file.write("grid on\r\n")

        save_file.write("\r\nfigure;\r\n")
        save_file.write("plot(sample_time*1000);\r\n")
        save_file.write("title('Sample Time.');\r\n")
        save_file.write("ylabel ( 'Sample Time (ms)' ) ;\r\n")
        save_file.write("xlabel ( 'Sample (k)' ) ;\r\n")
        save_file.write("grid on\r\n")

        save_file.close()
