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
        self.prev1 = 0
        self.prev2 = 0
        self.x_position = 0
        self.y_position = 0
        self.z_position = 0
        self.working = False

    def experiment_init(self, save_file, smooth, track_parameters):

        self.smooth_flag = smooth
        self.file_name = save_file
        self.experiment_reset()

        track_parameters['sample_time'] = self.sample_time

        self.reference.generate_track(**track_parameters)

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

    def experiment_save(self):

        for i in range(0, count - 1):
            x_position_dot_vector[i] = (x_position_vector[i + 1] - x_position_vector[i]) / \
                                       (time_vector[i + 1] - time_vector[i])
            y_position_dot_vector[i] = (y_position_vector[i + 1] - y_position_vector[i]) / \
                                       (time_vector[i + 1] - time_vector[i])
            z_position_dot_vector[i] = (z_position_vector[i + 1] - z_position_vector[i]) / \
                                       (time_vector[i + 1] - time_vector[i])

        x_position_dot_vector[count - 1] = x_position_dot_vector[count - 2]
        y_position_dot_vector[count - 1] = y_position_dot_vector[count - 2]
        z_position_dot_vector[count - 1] = z_position_dot_vector[count - 2]

        print("Sample time was not achieved: %4d times" % missed)
        print("Sample time was achieved:     %4d times" % accurate)
        print("Total:                        %4d times" % (missed + accurate))
        print("Total Expected:               %4d times" % len(x_position_vector))
        print("Worth sample time:            %12f ms" % (max_elapsed * 1000))
        print("Desired sample time:          %12f ms" % (desired * 1000))

        save_file = open(file_name, 'w')

        save_file.write("close all;\r\n")
        save_file.write("clear all;\r\n")
        save_file.write("clc;\r\n\r\n")

        save_file.write("count=%f;\r\n" % count)
        save_file.write("radius=%f;\r\n" % radius)
        save_file.write("distance=%f;\r\n" % distance)
        save_file.write("constant_b=%f;\r\n" % constant_b)
        save_file.write("constant_k1=%f;\r\n" % constant_k1)
        save_file.write("constant_k2=%f;\r\n" % constant_k2)
        save_file.write("constant_ki=%f;\r\n" % constant_ki)
        save_file.write("constant_kd=%f;\r\n" % constant_kd)
        save_file.write("constant_kc=%f;\r\n" % constant_kc)

        for i in range(0, count):
            save_file.write("speed1(%d) = %f ;\r\n" % (i + 1, value1[i]))
            save_file.write("speed2(%d) = %f ;\r\n" % (i + 1, value2[i]))
            save_file.write("current1(%d) = %f ;\r\n" % (i + 1, current1_vector[i]))
            save_file.write("current2(%d) = %f ;\r\n" % (i + 1, current2_vector[i]))
            save_file.write("time(%d) = %f ;\r\n" % (i + 1, time_vector[i]))
            save_file.write("sample_time(%d) = %f ;\r\n" % (i + 1, sample_time_vector[i]))
            save_file.write("ref1(%d) = %f ;\r\n" % (i + 1, reference1[i]))
            save_file.write("ref2(%d) = %f ;\r\n" % (i + 1, reference2[i]))
            save_file.write("x(%d) = %f ;\r\n" % (i + 1, x_position_vector[i]))
            save_file.write("y(%d) = %f ;\r\n" % (i + 1, y_position_vector[i]))
            save_file.write("z(%d) = %f ;\r\n" % (i + 1, z_position_vector[i]))
            save_file.write("xd(%d) = %f ;\r\n" % (i + 1, xd_vector[i]))
            save_file.write("yd(%d) = %f ;\r\n" % (i + 1, yd_vector[i]))
            save_file.write("zd(%d) = %f ;\r\n" % (i + 1, zd_vector[i]))
            save_file.write("dx(%d) = %f ;\r\n" % (i + 1, x_position_dot_vector[i]))
            save_file.write("dy(%d) = %f ;\r\n" % (i + 1, y_position_dot_vector[i]))
            save_file.write("dz(%d) = %f ;\r\n" % (i + 1, z_position_dot_vector[i]))
            save_file.write("dxd(%d) = %f ;\r\n" % (i + 1, xd_dot_vector[i]))
            save_file.write("dyd(%d) = %f ;\r\n" % (i + 1, yd_dot_vector[i]))
            save_file.write("dzd(%d) = %f ;\r\n" % (i + 1, zd_dot_vector[i]))
            save_file.write("dxr(%d) = %f ;\r\n" % (i + 1, x_ref_vector[i]))
            save_file.write("dyr(%d) = %f ;\r\n" % (i + 1, y_ref_vector[i]))

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
        g = globals()
        g['finished'] = False
        g['count'] = 0
        g['missed'] = 0
        g['accurate'] = 0
        g['max_elapsed'] = 0
        g['u1k1'] = 0
        g['u2k1'] = 0
        g['e1k1'] = 0
        g['e1k2'] = 0
        g['e2k1'] = 0
        g['e2k2'] = 0
        g['prev1'] = 0
        g['prev2'] = 0
        g['x_position'] = 0
        g['y_position'] = 0
        g['z_position'] = 0
        g['md25'].reset_encoders()


    def experiment_stop(self):
        global finished
        finished = True


    def experiment_emergency(self):
        global finished, working
        finished = True
        md25.drive_motors(0, 0)
        timer_stop()
        experiment_save()
        print 'Done'
        working = False

    def timer_handler(self, signum, frame):

        self.working = True

        now = time.time()
        elapsed = now - self.prev

        if self.finished:
            self.md25.drive_motors(0, 0)
            self.timer_stop()
            experiment_save()
            print 'Done'
            working = False
            return

        if count == 0:
            time_vector[0] = 0
        else:
            time_vector[count] = time_vector[count - 1] + elapsed
        sample_time_vector[count] = elapsed

        prev = now
        max_elapsed = elapsed if max_elapsed < elapsed else max_elapsed
        if elapsed > desired:
            missed += 1
        else:
            accurate += 1

        encoder1, encoder2, battery, current1, current2 = md25.read_state()
        md25.reset_encoders()

        if encoder1 > 130 or encoder1 < -130:
            encoder1 = prev1
            # TODO: can be removed
            md25.reset_encoders()
            return

        if encoder2 > 130 or encoder2 < -130:
            encoder2 = prev2
            md25.reset_encoders()
            return

        prev1 = encoder1
        prev2 = encoder2

        dfr = prev2 * 2 * math.pi / 360
        dfl = prev1 * 2 * math.pi / 360

        ds = (dfr + dfl) * radius / 2
        dz = (dfr - dfl) * radius / distance

        x_position += ds * math.cos(z_position + dz / 2)
        y_position += ds * math.sin(z_position + dz / 2)
        z_position += dz

        x_position_vector[count] = x_position
        y_position_vector[count] = y_position
        z_position_vector[count] = z_position

        xd = xd_vector[count]
        xd_dot = xd_dot_vector[count]
        yd = yd_vector[count]
        yd_dot = yd_dot_vector[count]

        zd = zd_vector[count]
        zd_dot = zd_dot_vector[count]

        y1 = x_position + constant_b * math.cos(z_position)
        y2 = y_position + constant_b * math.sin(z_position)

        if smooth_flag:
            y1d = xd
            y2d = yd
            y2d_dot = yd_dot
            y1d_dot = xd_dot
        else:
            y1d = xd + constant_b * math.cos(zd)
            y2d = yd + constant_b * math.sin(zd)

            y2d_dot = yd_dot + constant_b * math.cos(zd) * zd_dot
            y1d_dot = xd_dot - constant_b * math.sin(zd) * zd_dot

        u2 = y2d_dot + constant_k2 * (y2d - y2)
        u1 = y1d_dot + constant_k1 * (y1d - y1)

        x_ref_vector[count] = u1
        y_ref_vector[count] = u2

        the_v = math.cos(z_position) * u1 + u2 * math.sin(z_position)
        the_omega = u1 * (- math.sin(z_position) / constant_b) + u2 * math.cos(z_position) / constant_b

        set_point2 = the_v / radius + the_omega * distance / 2 / radius
        set_point1 = the_v / radius - the_omega * distance / 2 / radius

        steps_per_sec1 = encoder1 / elapsed
        angular_speed1 = steps_per_sec1 * 2 * math.pi / 360

        value1[count] = angular_speed1
        current1_vector[count] = current1
        reference1[count] = set_point1

        steps_per_sec2 = encoder2 / elapsed
        angular_speed2 = steps_per_sec2 * 2 * math.pi / 360

        value2[count] = angular_speed2
        current2_vector[count] = current2
        reference2[count] = set_point2

        count += 1

        if count >= len(xd_vector):
            finished = True

        e1k = set_point1 - angular_speed1

        if constant_ki == 0:
            uuu1 = e1k * constant_kc
        else:
            uuu1 = e1k * constant_kc + (constant_ki - constant_kc) * e1k1 + u1k1

        if constant_kd != 0:
            uuu1 = constant_kc * (e1k - e1k1) + constant_ki * e1k + u1k1 + constant_kd * (e1k - 2 * e1k1 + e1k2)

        u1k1 = uuu1
        e1k1 = e1k
        e1k2 = e1k1

        if uuu1 > 127:
            uuu1 = 127
        if uuu1 < - 128:
            uuu1 = - 128

        um1 = int(uuu1)

        e2k = (set_point2 - angular_speed2)

        if constant_ki == 0:
            uuu2 = e2k * constant_kc
        else:
            uuu2 = e2k * constant_kc + (constant_ki - constant_kc) * e2k1 + u2k1

        if constant_kd != 0:
            uuu2 = constant_kc * (e2k - e2k1) + constant_ki * e2k + u2k1 + constant_kd * (e2k - 2 * e2k1 + e2k2)

        u2k1 = uuu2
        e2k1 = e2k
        e2k2 = e2k1

        if uuu2 > 127:
            uuu2 = 127
        if uuu2 < - 128:
            uuu2 = - 128

        um2 = int(uuu2)

        md25.drive_motors(um1, um2)

        #TODO: send message

        working = False

    def timer_stop(self):
        signal.setitimer(signal.ITIMER_REAL, 0, 0)

    def timer_start(self):
        self.prev = time.time()
        signal.setitimer(signal.ITIMER_REAL, self.sample_time, self.sample_time)

    def timer_init(self):
        signal.signal(signal.SIGALRM, self.timer_handler)
        self.timer_stop()


md25 = board.MD25(1, 0x58)

radius = 0.05
distance = 0.2995
constant_b = 0.05
constant_k1 = 3.0
constant_k2 = 3.0
constant_ki = 1.0
constant_kd = 1.0
constant_kc = 2.0
desired = 0.05

missed = 0
accurate = 0
max_elapsed = 0
prev = 0
finished = True
count = 0
u1k1 = 0
u2k1 = 0
e1k1 = 0
e1k2 = 0
e2k1 = 0
e2k2 = 0
prev1 = 0
prev2 = 0
x_position = 0
y_position = 0
z_position = 0
file_name = ''
working = False
time_vector = []
sample_time_vector = []
x_position_vector = []
x_position_dot_vector = []
y_position_vector = []
y_position_dot_vector = []
z_position_vector = []
z_position_dot_vector = []
xd_vector = []
xd_dot_vector = []
yd_vector = []
yd_dot_vector = []
zd_vector = []
zd_dot_vector = []
smooth_flag = True
x_ref_vector = []
y_ref_vector = []
value1 = []
current1_vector = []
reference1 = []
value2 = []
current2_vector = []
reference2 = []


def experiment_init(save_file, smooth, track):
    global file_name, smooth_flag, xd_vector, yd_vector, zd_vector, xd_dot_vector, yd_dot_vector, zd_dot_vector, \
        time_vector, sample_time_vector, x_position_vector, y_position_vector, z_position_vector, x_ref_vector, \
        y_ref_vector, value1, current1_vector, reference1, value2, current2_vector, reference2, x_position_dot_vector, \
        y_position_dot_vector, z_position_dot_vector, desired

    smooth_flag = smooth
    file_name = save_file
    experiment_reset()

    xd_vector, yd_vector, zd_vector, xd_dot_vector, yd_dot_vector, zd_dot_vector = track.generate_track(**track)
    n_points = len(xd_vector)
    time_vector = range(0, n_points)
    sample_time_vector = range(0, n_points)
    x_position_vector = range(0, n_points)
    x_position_dot_vector = range(0, n_points)
    y_position_vector = range(0, n_points)
    y_position_dot_vector = range(0, n_points)
    z_position_vector = range(0, n_points)
    z_position_dot_vector = range(0, n_points)
    x_ref_vector = range(0, n_points)
    y_ref_vector = range(0, n_points)
    value1 = range(0, n_points)
    current1_vector = range(0, n_points)
    reference1 = range(0, n_points)
    value2 = range(0, n_points)
    current2_vector = range(0, n_points)
    reference2 = range(0, n_points)
    timer_start(desired)


def experiment_save():
    global count, radius, distance, constant_b, constant_k1, constant_k2, constant_ki, constant_kd, constant_kc, \
        x_position_dot_vector, y_position_dot_vector, z_position_dot_vector, x_position_vector, \
        y_position_vector, z_position_vector, time_vector, missed, accurate, max_elapsed, desired, \
        file_name, value1, value2, current1_vector, current2_vector, sample_time_vector, reference1, \
        reference2, xd_vector, yd_vector, zd_vector, x_ref_vector, y_ref_vector, xd_dot_vector, yd_dot_vector, \
        zd_dot_vector

    for i in range(0, count - 1):
        x_position_dot_vector[i] = (x_position_vector[i + 1] - x_position_vector[i]) / \
                                   (time_vector[i + 1] - time_vector[i])
        y_position_dot_vector[i] = (y_position_vector[i + 1] - y_position_vector[i]) / \
                                   (time_vector[i + 1] - time_vector[i])
        z_position_dot_vector[i] = (z_position_vector[i + 1] - z_position_vector[i]) / \
                                   (time_vector[i + 1] - time_vector[i])

    x_position_dot_vector[count - 1] = x_position_dot_vector[count - 2]
    y_position_dot_vector[count - 1] = y_position_dot_vector[count - 2]
    z_position_dot_vector[count - 1] = z_position_dot_vector[count - 2]

    print("Sample time was not achieved: %4d times" % missed)
    print("Sample time was achieved:     %4d times" % accurate)
    print("Total:                        %4d times" % (missed + accurate))
    print("Total Expected:               %4d times" % len(x_position_vector))
    print("Worth sample time:            %12f ms" % (max_elapsed * 1000))
    print("Desired sample time:          %12f ms" % (desired * 1000))

    save_file = open(file_name, 'w')

    save_file.write("close all;\r\n")
    save_file.write("clear all;\r\n")
    save_file.write("clc;\r\n\r\n")

    save_file.write("count=%f;\r\n" % count)
    save_file.write("radius=%f;\r\n" % radius)
    save_file.write("distance=%f;\r\n" % distance)
    save_file.write("constant_b=%f;\r\n" % constant_b)
    save_file.write("constant_k1=%f;\r\n" % constant_k1)
    save_file.write("constant_k2=%f;\r\n" % constant_k2)
    save_file.write("constant_ki=%f;\r\n" % constant_ki)
    save_file.write("constant_kd=%f;\r\n" % constant_kd)
    save_file.write("constant_kc=%f;\r\n" % constant_kc)

    for i in range(0, count):
        save_file.write("speed1(%d) = %f ;\r\n" % (i + 1, value1[i]))
        save_file.write("speed2(%d) = %f ;\r\n" % (i + 1, value2[i]))
        save_file.write("current1(%d) = %f ;\r\n" % (i + 1, current1_vector[i]))
        save_file.write("current2(%d) = %f ;\r\n" % (i + 1, current2_vector[i]))
        save_file.write("time(%d) = %f ;\r\n" % (i + 1, time_vector[i]))
        save_file.write("sample_time(%d) = %f ;\r\n" % (i + 1, sample_time_vector[i]))
        save_file.write("ref1(%d) = %f ;\r\n" % (i + 1, reference1[i]))
        save_file.write("ref2(%d) = %f ;\r\n" % (i + 1, reference2[i]))
        save_file.write("x(%d) = %f ;\r\n" % (i + 1, x_position_vector[i]))
        save_file.write("y(%d) = %f ;\r\n" % (i + 1, y_position_vector[i]))
        save_file.write("z(%d) = %f ;\r\n" % (i + 1, z_position_vector[i]))
        save_file.write("xd(%d) = %f ;\r\n" % (i + 1, xd_vector[i]))
        save_file.write("yd(%d) = %f ;\r\n" % (i + 1, yd_vector[i]))
        save_file.write("zd(%d) = %f ;\r\n" % (i + 1, zd_vector[i]))
        save_file.write("dx(%d) = %f ;\r\n" % (i + 1, x_position_dot_vector[i]))
        save_file.write("dy(%d) = %f ;\r\n" % (i + 1, y_position_dot_vector[i]))
        save_file.write("dz(%d) = %f ;\r\n" % (i + 1, z_position_dot_vector[i]))
        save_file.write("dxd(%d) = %f ;\r\n" % (i + 1, xd_dot_vector[i]))
        save_file.write("dyd(%d) = %f ;\r\n" % (i + 1, yd_dot_vector[i]))
        save_file.write("dzd(%d) = %f ;\r\n" % (i + 1, zd_dot_vector[i]))
        save_file.write("dxr(%d) = %f ;\r\n" % (i + 1, x_ref_vector[i]))
        save_file.write("dyr(%d) = %f ;\r\n" % (i + 1, y_ref_vector[i]))

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


def experiment_reset():
    g = globals()
    g['finished'] = False
    g['count'] = 0
    g['missed'] = 0
    g['accurate'] = 0
    g['max_elapsed'] = 0
    g['u1k1'] = 0
    g['u2k1'] = 0
    g['e1k1'] = 0
    g['e1k2'] = 0
    g['e2k1'] = 0
    g['e2k2'] = 0
    g['prev1'] = 0
    g['prev2'] = 0
    g['x_position'] = 0
    g['y_position'] = 0
    g['z_position'] = 0
    g['md25'].reset_encoders()


def experiment_stop():
    global finished
    finished = True


def experiment_emergency():
    global finished, working
    finished = True
    md25.drive_motors(0, 0)
    timer_stop()
    experiment_save()
    print 'Done'
    working = False


def timer_handler(signum, frame):
    global working, finished, prev, count, time_vector, max_elapsed, desired, missed, accurate, sample_time_vector, \
        prev1, prev2, radius, distance, x_position, y_position, z_position, u1k1, u2k1, e1k1, e1k2, e2k1, e2k2, \
        x_position_vector, y_position_vector, z_position_vector, xd_vector, xd_dot_vector, yd_vector, yd_dot_vector, \
        zd_vector, zd_dot_vector, smooth_flag, constant_b, constant_k1, constant_k2, radius, distance, x_ref_vector, \
        y_ref_vector, value1, current1_vector, reference1, value2, current2_vector, reference2, constant_ki, \
        constant_ki, constant_kc, md25

    working = True

    now = time.time()
    elapsed = now - prev

    if finished:
        md25.drive_motors(0, 0)
        timer_stop()
        experiment_save()
        print 'Done'
        working = False
        return

    if count == 0:
        time_vector[0] = 0
    else:
        time_vector[count] = time_vector[count - 1] + elapsed
    sample_time_vector[count] = elapsed

    prev = now
    max_elapsed = elapsed if max_elapsed < elapsed else max_elapsed
    if elapsed > desired:
        missed += 1
    else:
        accurate += 1

    encoder1, encoder2, battery, current1, current2 = md25.read_state()
    md25.reset_encoders()

    if encoder1 > 130 or encoder1 < -130:
        encoder1 = prev1
        # TODO: can be removed
        md25.reset_encoders()
        return

    if encoder2 > 130 or encoder2 < -130:
        encoder2 = prev2
        md25.reset_encoders()
        return

    prev1 = encoder1
    prev2 = encoder2

    dfr = prev2 * 2 * math.pi / 360
    dfl = prev1 * 2 * math.pi / 360

    ds = (dfr + dfl) * radius / 2
    dz = (dfr - dfl) * radius / distance

    x_position += ds * math.cos(z_position + dz / 2)
    y_position += ds * math.sin(z_position + dz / 2)
    z_position += dz

    x_position_vector[count] = x_position
    y_position_vector[count] = y_position
    z_position_vector[count] = z_position

    xd = xd_vector[count]
    xd_dot = xd_dot_vector[count]
    yd = yd_vector[count]
    yd_dot = yd_dot_vector[count]

    zd = zd_vector[count]
    zd_dot = zd_dot_vector[count]

    y1 = x_position + constant_b * math.cos(z_position)
    y2 = y_position + constant_b * math.sin(z_position)

    if smooth_flag:
        y1d = xd
        y2d = yd
        y2d_dot = yd_dot
        y1d_dot = xd_dot
    else:
        y1d = xd + constant_b * math.cos(zd)
        y2d = yd + constant_b * math.sin(zd)

        y2d_dot = yd_dot + constant_b * math.cos(zd) * zd_dot
        y1d_dot = xd_dot - constant_b * math.sin(zd) * zd_dot

    u2 = y2d_dot + constant_k2 * (y2d - y2)
    u1 = y1d_dot + constant_k1 * (y1d - y1)

    x_ref_vector[count] = u1
    y_ref_vector[count] = u2

    the_v = math.cos(z_position) * u1 + u2 * math.sin(z_position)
    the_omega = u1 * (- math.sin(z_position) / constant_b) + u2 * math.cos(z_position) / constant_b

    set_point2 = the_v / radius + the_omega * distance / 2 / radius
    set_point1 = the_v / radius - the_omega * distance / 2 / radius

    steps_per_sec1 = encoder1 / elapsed
    angular_speed1 = steps_per_sec1 * 2 * math.pi / 360

    value1[count] = angular_speed1
    current1_vector[count] = current1
    reference1[count] = set_point1

    steps_per_sec2 = encoder2 / elapsed
    angular_speed2 = steps_per_sec2 * 2 * math.pi / 360

    value2[count] = angular_speed2
    current2_vector[count] = current2
    reference2[count] = set_point2

    count += 1

    if count >= len(xd_vector):
        finished = True

    e1k = set_point1 - angular_speed1

    if constant_ki == 0:
        uuu1 = e1k * constant_kc
    else:
        uuu1 = e1k * constant_kc + (constant_ki - constant_kc) * e1k1 + u1k1

    if constant_kd != 0:
        uuu1 = constant_kc * (e1k - e1k1) + constant_ki * e1k + u1k1 + constant_kd * (e1k - 2 * e1k1 + e1k2)

    u1k1 = uuu1
    e1k1 = e1k
    e1k2 = e1k1

    if uuu1 > 127:
        uuu1 = 127
    if uuu1 < - 128:
        uuu1 = - 128

    um1 = int(uuu1)

    e2k = (set_point2 - angular_speed2)

    if constant_ki == 0:
        uuu2 = e2k * constant_kc
    else:
        uuu2 = e2k * constant_kc + (constant_ki - constant_kc) * e2k1 + u2k1

    if constant_kd != 0:
        uuu2 = constant_kc * (e2k - e2k1) + constant_ki * e2k + u2k1 + constant_kd * (e2k - 2 * e2k1 + e2k2)

    u2k1 = uuu2
    e2k1 = e2k
    e2k2 = e2k1

    if uuu2 > 127:
        uuu2 = 127
    if uuu2 < - 128:
        uuu2 = - 128

    um2 = int(uuu2)

    md25.drive_motors(um1, um2)

    #TODO: send message

    working = False


def timer_stop():
    signal.setitimer(signal.ITIMER_REAL, 0, 0)


def timer_start(sample_time):
    global prev, desired
    desired = sample_time
    prev = time.time()
    signal.setitimer(signal.ITIMER_REAL, desired, desired)


def timer_init():
    signal.signal(signal.SIGALRM, timer_handler)
    timer_stop()
