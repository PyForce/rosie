from modules.kernel import kernel

ordex = None
command = None


def _ordex(rdx):
    global ordex, command
    ordex = rdx
    command = ordex.Command()


def get_odometry():
    p = kernel.ROBOT.position()
    return (-p[0], p[1], p[2])


def get_metadata():
    return ''


def get_sensor(name=''):
    return []


def set_position(X=0, Y=0, theta=0):
    kernel.ROBOT.position(X, Y, theta)


def process_text(text=""):
    if ordex:
        print(' Processing text: %s' % repr(text))
        cmd = command.extraction(text)
        if isinstance(cmd, ordex.base.Common_Commands):
            for item in cmd.CMD:
                kernel.sync_exec(item)
    else:
        print("ALERT: NLP module isn't configured")


def set_keys(keys=[]):
    kernel.KEYS = keys


def set_mode(mode=''):
    if mode == 'manual':
        kernel.mode('USER')
    else:
        kernel.mode('KERNEL')


def set_path(path=[]):
    tmp = []
    for item in path:
        tmp.append(tuple(item))
    path = tmp

    cmd = {'start': None, 'end': None, 'path': path, 'action': 'stop'}
    kernel.sync_exec(cmd)


def set_position_notifier(notifier):
    print("connecting robot with server notifier")
    kernel.ROBOT.controller.SEND_POSITION = notifier


def send_updated_position(pos):
    # send position
    # print(pos)
    pass


def get_profile():
    return kernel.ROBOT.profile()
