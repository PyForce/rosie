from robot import Robot
from tools.FileNameProvider import FileNameProviderByTime
from .filelogger import FileLoggerMovementSupervisor

def init():
    r = Robot()
    r.motion.movement_supervisor.append(FileLoggerMovementSupervisor(r.setting_handler.parameters,
                                                                         FileNameProviderByTime()))

