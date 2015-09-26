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
except Exception as e:
    print(e)
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


def trivial(message):
        print('In message:')
        print('type', message.mtype)
        print('cmd', message.cmd)
        print('args', message.args)


class Protocol:

    @staticmethod
    def exec_set_speed(message, my_socket, client_socket):
        trivial(message)
        print('exec_set_speed')

    @staticmethod
    def exec_set_position(message, my_socket, client_socket):
        trivial(message)
        print('exec_set_position')

    @staticmethod
    def exec_set_path(message, my_socket, client_socket):
        trivial(message)
        print('exec_set_path')

    @staticmethod
    def exec_set_command(message, my_socket, client_socket):
        trivial(message)
        print('exec_set_command')

        cmd = command.extraction(message.args[0].decode())
        if isinstance(cmd, ordex.base.Common_Commands):
            print(cmd.CMD)
            kernel.execute(cmd.CMD)
        elif isinstance(cmd, ordex.base.Urgent_Commands):
            pass
        else:
            print("ERROR")

    @staticmethod
    def exec_set_wasd(message, my_socket, client_socket):
        trivial(message)
        print('exec_set_wasd')

    @staticmethod
    def exec_set_update(message, my_socket, client_socket):
        trivial(message)
        print('exec_set_update')

    @staticmethod
    def reply(message, my_socket, client_socket, argv):
        nw_message = ptcl.message()
        nw_message.new("reply", message.cmd, argv)
        my_socket.sendto(nw_message.toString(), client_socket)

    @staticmethod
    def exec_get_speed(message, my_socket, client_socket):
        trivial(message)

        print('exec_get_speed')

    @staticmethod
    def exec_get_sensor(message, my_socket, client_socket):
        trivial(message)
        print('exec_get_sensor')

    @staticmethod
    def exec_get_odometry(message, my_socket, client_socket):
        trivial(message)
        print('exec_get_odometry')

        # TODO: Change for the real functionality
        from random import Random
        r = Random()
        a, b, c = [r.randint(1, 255) for i in range(3)]
        odometry = [a, b, c]

        Protocol.reply(message, my_socket, client_socket, odometry)

    @staticmethod
    def exec_get_photo(message, my_socket, client_socket):
        trivial(message)
        print('exec_get_photo')

    @staticmethod
    def exec_get_video_stream(message, my_socket, client_socket):
        trivial(message)
        print('exec_get_video_stream')

    @staticmethod
    def exec_get_audio_stream(message, my_socket, client_socket):
        trivial(message)
        print('exec_get_audio_stream')


protocol = Protocol()


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
        func = getattr(protocol, "exec_%s_%s" % (message.mtype, message.cmd))
        func(message, s, self.client_address)

        #decMessage.FromString(message.message_data)
        #print(decMessage.command)
        #message = message.decode()


class ThreadedServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    """
    Receives and send messages in separate threads
    """
    pass
