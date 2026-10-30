from rosie.file_names import FileNameProviderByTime
from rosie.extensions.file_logger.file_logger import FileLoggerMovementSupervisor


async def run(robot, settings):
    robot.motion.movement_supervisor.append(FileLoggerMovementSupervisor(robot.setting_handler.parameters,
                                                                         FileNameProviderByTime()))
