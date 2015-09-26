# version 1.0
types = [
    "set",
    "get",
    "reply"
]

get_commands = {
    'speed': 'exec_get_speed',
    'sensor': 'exec_get_sensor',
    'odometry': 'exec_get_odometry',
    'photo': 'exec_get_photo',
    'video_stream': 'exec_get_video_stream',
    'audio_stream': 'exec_get_audio_stream',
    'map': 'exec_get_map'
}

set_commands = {
    'speed': 'exec_set_speed',
    'position': 'exec_set_position',
    'path': 'exec_set_path',
    'command': 'exec_set_command',
    'wasd': 'exec_set_wasd',
    'update': 'exec_set_update',
    'map': 'exec_set_map'
}

reply_commands = {
    'speed': 'exec_reply_speed',
    'sensor': 'exec_reply_sensor',
    'odometry': 'exec_reply_odometry',
    'photo': 'exec_reply_photo',
    'video_stream': 'exec_reply_video_stream',
    'audio_stream': 'exec_reply_audio_stream',
    'map': 'exec_reply_map'
}


class message():
    def __init__(self):
        self.reset()

    def reset(self):
        self.mtype = None
        self.cmd = None
        self.args = None

    def new(self, mtype, cmd, args):
        if self.validate(mtype, cmd):
            self.mtype = mtype
            self.cmd = cmd
            self.args = args

    def validate(self, mtype, cmd):
        return mtype in types and \
            (mtype == types[0] and cmd in set_commands) or \
            (mtype == types[1] and cmd in get_commands) or \
            (mtype == types[2] and cmd in reply_commands)

    def toString(self):
        return self.mtype + "|" + self.cmd + "|" + str([self.args])

    def fromString(self, string):
        splited = string.split("|")
        tstring = ""
        self.new(splited[0], splited[1], eval(tstring.join(splited[2:])))

m = message()
m.new("set", "position", [2, 3, 4])
s = m.toString()

m2 = message()
m2.fromString(s)
