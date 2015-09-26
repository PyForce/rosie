import SocketServer


print('Importing module: communication...')
try:
    from modules.communication import ptcl
    print('communication... Ok')
except Exception as e:
    print(e)
    print('communication... Fail')


print('Importing module: ordex...')
try:
    from modules import ordex
    print('ordex... Ok')
except:
    print('ordex... Fail')


print('Importing module: kernel...')
try:
    from modules.kernel import kernel
    print('kernel... Ok')
except Exception as e:
    print(e)
    print('kernel... Fail')

command = ordex.Command()
command.draw_syntactic_trees(False)

def trivial(data):
    print('In data:')
    print('type', data.mtype)
    print('cmd', data.cmd)
    print('args', data.args)


def exec_set_speed(data):
    trivial(data)
    print('exec_set_speed')


def exec_set_position(data):
    trivial(data)
    print('exec_set_position')


def exec_set_path(data):
    trivial(data)
    print('exec_set_path')


def exec_set_command(data):
    trivial(data)
    print(exec_set_command)

    cmd = command.extraction(data.args[0].decode())
    if isinstance(cmd, ordex.base.Common_Commands):
        print(cmd.CMD)
        kernel.execute(cmd.CMD)
    elif isinstance(cmd, ordex.base.Urgent_Commands):
        pass
    else:
        print("ERROR")


def exec_set_wasd(data):
    trivial(data)
    print('exec_set_wasd')


def exec_set_update(data):
    trivial(data)
    print('exec_set_update')


def exec_get_speed(data):
    trivial(data)
    print('exec_get_speed')


def exec_get_sensor(data):
    trivial(data)
    print('exec_get_sensor')


def exec_get_odometry(data):
    trivial(data)
    print('exec_get_odometry')


def exec_get_photo(data):
    trivial(data)
    print('exec_get_photo')


def exec_get_video_stream(data):
    trivial(data)
    print('exec_get_video_stream')


def exec_get_audio_stream(data):
    trivial(data)
    print('exec_get_audio_stream')


EVALUATOR = {
    'set_speed': exec_set_speed,
    'set_position': exec_set_position,
    'set_path': exec_set_path,
    'set_command': exec_set_command,
    'set_wasd': exec_set_wasd,
    'set_update': exec_set_update,

    'get_speed': exec_get_speed,
    'get_sensor': exec_get_sensor,
    'get_odometry': exec_get_odometry,
    'get_photo': exec_get_photo,
    'get_video_stream': exec_get_video_stream,
    'get_audio_stream': exec_get_audio_stream
}


class UDPHandler(SocketServer.BaseRequestHandler):
    """
        Handles the messages coming from HUD
    """

    def handle(self):
        data, s = self.request
        print('From %s arrive: \"%s\"' % (s.getsockname(), data))

        message = ptcl.message()
        message.fromString(data)

        # Call the functions from the dictionary
        # depends of the name of decMessage.type
        EVALUATOR["%s_%s" % (message.mtype, message.cmd)](message)

        #decMessage.FromString(message.message_data)
        #print(decMessage.command)
        #message = message.decode()


class ThreadedServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    """
        Receives and send messages in separate threads
    """
    pass

