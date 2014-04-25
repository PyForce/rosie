import math
import signal
import board
import time
import track


class Controller:
    def __init__(self):
        self.md25 = board.MD25(1, 0x58)
        self.reference = track.Track()
        self.time_vector = []
        self.sample_time_vector = []
        self.x_position_vector = []
        self.x_position_dot_vector = []
        self.y_position_vector = []
        self.y_position_dot_vector = []
        self.z_position_vector = []
        self.z_position_dot_vector = []
        self.smooth_flag = True
        self.x_ref_vector = []
        self.y_ref_vector = []
        self.value1 = []
        self.current1_vector = []
        self.reference1 = []
        self.value2 = []
        self.current2_vector = []
        self.reference2 = []
        self.file_name = ''

        self.radius = 0.05
        self.distance = 0.2995
        self.constant_b = 0.05
        self.constant_k1 = 3.0
        self.constant_k2 = 3.0
        self.constant_ki = 1.0
        self.constant_kd = 1.0
        self.constant_kc = 2.0
        self.sample_time = 0.05

        self.missed = 0
        self.accurate = 0
        self.max_elapsed = 0
        self.prev = 0
        self.finished = True
        self.count = 0
        self.u1k1 = 0
        self.u2k1 = 0
        self.e1k1 = 0
        self.e1k2 = 0
        self.e2k1 = 0
        self.e2k2 = 0
        self.x_position = 0
        self.y_position = 0
        self.z_position = 0
        self.working = False

        self.timer_init()

    def experiment_init(self, save_file, smooth, track_parameters):

        self.smooth_flag = smooth
        self.file_name = save_file
        self.experiment_reset()

        track_parameters['sample_time'] = self.sample_time

        self.reference.generate(**track_parameters)

        self.time_vector = range(self.reference.n_points)
        self.sample_time_vector = range(self.reference.n_points)
        self.x_position_vector = range(self.reference.n_points)
        self.x_position_dot_vector = range(self.reference.n_points)
        self.y_position_vector = range(self.reference.n_points)
        self.y_position_dot_vector = range(self.reference.n_points)
        self.z_position_vector = range(self.reference.n_points)
        self.z_position_dot_vector = range(self.reference.n_points)
        self.x_ref_vector = range(self.reference.n_points)
        self.y_ref_vector = range(self.reference.n_points)
        self.value1 = range(self.reference.n_points)
        self.current1_vector = range(self.reference.n_points)
        self.reference1 = range(self.reference.n_points)
        self.value2 = range(self.reference.n_points)
        self.current2_vector = range(self.reference.n_points)
        self.reference2 = range(self.reference.n_points)
        self.timer_start()

    def experiment_finish(self):
        self.md25.drive_motors(0, 0)
        signal.setitimer(signal.ITIMER_REAL, 0, 0)
        self.experiment_save()
        print 'Done'
        self.working = False
        self.finished = True

    def experiment_save(self):

        for i in range(0, self.count - 1):
            self.x_position_dot_vector[i] = (self.x_position_vector[i + 1] - self.x_position_vector[i]) / \
                                            (self.time_vector[i + 1] - self.time_vector[i])
            self.y_position_dot_vector[i] = (self.y_position_vector[i + 1] - self.y_position_vector[i]) / \
                                            (self.time_vector[i + 1] - self.time_vector[i])
            self.z_position_dot_vector[i] = (self.z_position_vector[i + 1] - self.z_position_vector[i]) / \
                                            (self.time_vector[i + 1] - self.time_vector[i])

        self.x_position_dot_vector[self.count - 1] = self.x_position_dot_vector[self.count - 2]
        self.y_position_dot_vector[self.count - 1] = self.y_position_dot_vector[self.count - 2]
        self.z_position_dot_vector[self.count - 1] = self.z_position_dot_vector[self.count - 2]

        print("Sample time was not achieved: %4d times" % self.missed)
        print("Sample time was achieved:     %4d times" % self.accurate)
        print("Total:                        %4d times" % (self.missed + self.accurate))
        print("Total Expected:               %4d times" % self.reference.n_points)
        print("Worth sample time:            %12f ms" % (self.max_elapsed * 1000))
        print("Desired sample time:          %12f ms" % (self.sample_time * 1000))

        save_file = open(self.file_name, 'w')

        save_file.write("close all;\r\n")
        save_file.write("clear all;\r\n")
        save_file.write("clc;\r\n\r\n")

        save_file.write("count=%f;\r\n" % self.count)
        save_file.write("radius=%f;\r\n" % self.radius)
        save_file.write("distance=%f;\r\n" % self.distance)
        save_file.write("constant_b=%f;\r\n" % self.constant_b)
        save_file.write("constant_k1=%f;\r\n" % self.constant_k1)
        save_file.write("constant_k2=%f;\r\n" % self.constant_k2)
        save_file.write("constant_ki=%f;\r\n" % self.constant_ki)
        save_file.write("constant_kd=%f;\r\n" % self.constant_kd)
        save_file.write("constant_kc=%f;\r\n" % self.constant_kc)

        for i in range(0, self.count):
            save_file.write("speed1(%d) = %f ;\r\n" % (i + 1, self.value1[i]))
            save_file.write("speed2(%d) = %f ;\r\n" % (i + 1, self.value2[i]))
            save_file.write("current1(%d) = %f ;\r\n" % (i + 1, self.current1_vector[i]))
            save_file.write("current2(%d) = %f ;\r\n" % (i + 1, self.current2_vector[i]))
            save_file.write("time(%d) = %f ;\r\n" % (i + 1, self.time_vector[i]))
            save_file.write("sample_time(%d) = %f ;\r\n" % (i + 1, self.sample_time_vector[i]))
            save_file.write("ref1(%d) = %f ;\r\n" % (i + 1, self.reference1[i]))
            save_file.write("ref2(%d) = %f ;\r\n" % (i + 1, self.reference2[i]))
            save_file.write("x(%d) = %f ;\r\n" % (i + 1, self.x_position_vector[i]))
            save_file.write("y(%d) = %f ;\r\n" % (i + 1, self.y_position_vector[i]))
            save_file.write("z(%d) = %f ;\r\n" % (i + 1, self.z_position_vector[i]))
            save_file.write("xd(%d) = %f ;\r\n" % (i + 1, self.reference.xd_vector[i]))
            save_file.write("yd(%d) = %f ;\r\n" % (i + 1, self.reference.yd_vector[i]))
            save_file.write("zd(%d) = %f ;\r\n" % (i + 1, self.reference.zd_vector[i]))
            save_file.write("dx(%d) = %f ;\r\n" % (i + 1, self.x_position_dot_vector[i]))
            save_file.write("dy(%d) = %f ;\r\n" % (i + 1, self.y_position_dot_vector[i]))
            save_file.write("dz(%d) = %f ;\r\n" % (i + 1, self.z_position_dot_vector[i]))
            save_file.write("dxd(%d) = %f ;\r\n" % (i + 1, self.reference.xd_dot_vector[i]))
            save_file.write("dyd(%d) = %f ;\r\n" % (i + 1, self.reference.yd_dot_vector[i]))
            save_file.write("dzd(%d) = %f ;\r\n" % (i + 1, self.reference.zd_dot_vector[i]))
            save_file.write("dxr(%d) = %f ;\r\n" % (i + 1, self.x_ref_vector[i]))
            save_file.write("dyr(%d) = %f ;\r\n" % (i + 1, self.y_ref_vector[i]))

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

    def experiment_reset(self):
        self.finished = False
        self.count = 0
        self.missed = 0
        self.accurate = 0
        self.max_elapsed = 0
        self.u1k1 = 0
        self.u2k1 = 0
        self.e1k1 = 0
        self.e1k2 = 0
        self.e2k1 = 0
        self.e2k2 = 0
        self.x_position = 0
        self.y_position = 0
        self.z_position = 0
        self.md25.reset_encoders()

    def timer_handler(self, signum, frame):

        self.working = True

        now = time.time()
        elapsed = now - self.prev

        if self.finished:
            self.experiment_finish()
            return

        if self.count == 0:
            self.time_vector[0] = 0
        else:
            self.time_vector[self.count] = self.time_vector[self.count - 1] + elapsed
        self.sample_time_vector[self.count] = elapsed

        self.prev = now
        self.max_elapsed = elapsed if self.max_elapsed < elapsed else self.max_elapsed
        if elapsed > self.sample_time:
            self.missed += 1
        else:
            self.accurate += 1

        encoder1, encoder2, battery, current1, current2 = self.md25.read_state()
        self.md25.reset_encoders()

        if encoder1 > 130 or encoder1 < -130:
            return

        if encoder2 > 130 or encoder2 < -130:
            return

        dfr = encoder2 * 2 * math.pi / 360
        dfl = encoder1 * 2 * math.pi / 360

        ds = (dfr + dfl) * self.radius / 2
        dz = (dfr - dfl) * self.radius / self.distance

        self.x_position += ds * math.cos(self.z_position + dz / 2)
        self.y_position += ds * math.sin(self.z_position + dz / 2)
        self.z_position += dz

        self.x_position_vector[self.count] = self.x_position
        self.y_position_vector[self.count] = self.y_position
        self.z_position_vector[self.count] = self.z_position

        xd = self.reference.xd_vector[self.count]
        xd_dot = self.reference.xd_dot_vector[self.count]
        yd = self.reference.yd_vector[self.count]
        yd_dot = self.reference.yd_dot_vector[self.count]

        zd = self.reference.zd_vector[self.count]
        zd_dot = self.reference.zd_dot_vector[self.count]

        y1 = self.x_position + self.constant_b * math.cos(self.z_position)
        y2 = self.y_position + self.constant_b * math.sin(self.z_position)

        if self.smooth_flag:
            y1d = xd
            y2d = yd
            y2d_dot = yd_dot
            y1d_dot = xd_dot
        else:
            y1d = xd + self.constant_b * math.cos(zd)
            y2d = yd + self.constant_b * math.sin(zd)

            y2d_dot = yd_dot + self.constant_b * math.cos(zd) * zd_dot
            y1d_dot = xd_dot - self.constant_b * math.sin(zd) * zd_dot

        u2 = y2d_dot + self.constant_k2 * (y2d - y2)
        u1 = y1d_dot + self.constant_k1 * (y1d - y1)

        self.x_ref_vector[self.count] = u1
        self.y_ref_vector[self.count] = u2

        the_v = math.cos(self.z_position) * u1 + u2 * math.sin(self.z_position)
        the_omega = u1 * (- math.sin(self.z_position) / self.constant_b) + u2 * math.cos(
            self.z_position) / self.constant_b

        set_point2 = the_v / self.radius + the_omega * self.distance / 2 / self.radius
        set_point1 = the_v / self.radius - the_omega * self.distance / 2 / self.radius

        steps_per_sec1 = encoder1 / elapsed
        angular_speed1 = steps_per_sec1 * 2 * math.pi / 360

        self.value1[self.count] = angular_speed1
        self.current1_vector[self.count] = current1
        self.reference1[self.count] = set_point1

        steps_per_sec2 = encoder2 / elapsed
        angular_speed2 = steps_per_sec2 * 2 * math.pi / 360

        self.value2[self.count] = angular_speed2
        self.current2_vector[self.count] = current2
        self.reference2[self.count] = set_point2

        self.count += 1

        if self.count >= self.reference.n_points:
            self.finished = True

        e1k = set_point1 - angular_speed1

        if self.constant_ki == 0:
            uuu1 = e1k * self.constant_kc
        else:
            uuu1 = e1k * self.constant_kc + (self.constant_ki - self.constant_kc) * self.e1k1 + self.u1k1

        if self.constant_kd != 0:
            uuu1 = self.constant_kc * (e1k - self.e1k1) + self.constant_ki * e1k + self.u1k1 + self.constant_kd * (
                e1k - 2 * self.e1k1 + self.e1k2)

        self.u1k1 = uuu1
        self.e1k2 = self.e1k1
        self.e1k1 = e1k

        if uuu1 > 127:
            uuu1 = 127
        if uuu1 < - 128:
            uuu1 = - 128

        um1 = int(uuu1)

        e2k = (set_point2 - angular_speed2)

        if self.constant_ki == 0:
            uuu2 = e2k * self.constant_kc
        else:
            uuu2 = e2k * self.constant_kc + (self.constant_ki - self.constant_kc) * self.e2k1 + self.u2k1

        if self.constant_kd != 0:
            uuu2 = self.constant_kc * (e2k - self.e2k1) + self.constant_ki * e2k + self.u2k1 + self.constant_kd * (
                e2k - 2 * self.e2k1 + self.e2k2)

        self.u2k1 = uuu2
        self.e2k2 = self.e2k1
        self.e2k1 = e2k

        if uuu2 > 127:
            uuu2 = 127
        if uuu2 < - 128:
            uuu2 = - 128

        um2 = int(uuu2)

        self.md25.drive_motors(um1, um2)

        #TODO: send message

        self.working = False

    def timer_start(self):
        self.prev = time.time()
        signal.setitimer(signal.ITIMER_REAL, self.sample_time, self.sample_time)

    def timer_init(self):
        signal.signal(signal.SIGALRM, self.timer_handler)
        signal.setitimer(signal.ITIMER_REAL, 0, 0)
