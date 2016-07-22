__author__ = 'Silvio'


class DifferentialDriveRobotSpeed:
    """
    Structure containing speeds of a robot

    @param x_speed: Component of the speed on the X axis
    @type x_speed: float
    @param y_speed: Component of the speed on the Y axis
    @type x_speed: float
    @param z_speed: Component of the speed on the Z axis (angular speed)
    @type x_speed: float
    """

    def __init__(self, x_speed=0., y_speed=0., z_speed=0.):
        self.z_speed = z_speed
        self.y_speed = y_speed
        self.x_speed = x_speed
