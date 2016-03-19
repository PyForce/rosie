from modules.kernel import kernel
from modules import ordex

command = ordex.Command()


def get_odometry():
    p=kernel.ROBOT.position()
    return (-p[0],p[1],p[2])

def get_metadata():
    return ''


def get_sensor(name=''):
    return []


def set_position(X=0, Y=0, theta=0):
    kernel.ROBOT.position(X, Y, theta)


def process_text(text=""):
    print(' Processing text: %s' % repr(text))
    cmd = command.extraction(text)
    if isinstance(cmd, ordex.base.Common_Commands):
        for item in cmd.CMD:
            kernel.sync_exec(item)

def set_keys(keys=[]):
    kernel.KEYS = keys


def set_mode(mode=''):
    if mode == 'manual':
        kernel.mode('USER')
    else:
        kernel.mode('KERNEL')


def set_path(path=[]):
    cmd = {'start': None, 'end': None, 'path': path, 'action': 'stop'}
    kernel.sync_exec(cmd)

def set_position_notifier(notifier):
    print("connecting robot with server notifier")
    print(kernel.ROBOT.controller.SEND_POSITION)
    kernel.ROBOT.controller.SEND_POSITION = notifier
    print(kernel.ROBOT.controller.SEND_POSITION)

def send_updated_position(pos):
    # send position
    # print(pos)
    pass
