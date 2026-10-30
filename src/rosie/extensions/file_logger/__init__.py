from rosie.robot import Robot
from rosie.file_names import FileNameProviderByTime
from rosie.extensions.file_logger.file_logger import FileLoggerMovementSupervisor


def init():
    r = Robot()
    r.motion.movement_supervisor.append(FileLoggerMovementSupervisor(r.setting_handler.parameters,
                                                                         FileNameProviderByTime()))
