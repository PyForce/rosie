__author__ = 'Silvio'


class DifferentialDriveRobotLocation:
    """
    Structure containing the cartesian coordinates of a robot

    @param x_position: Position on the X axis
    @param y_position: Position on the Y axis
    @param z_position: Position on the Z axis (angle, pose)
    """

    def __init__(self, x_position=0., y_position=0., z_position=0.):
        self.z_position = z_position
        self.y_position = y_position
        self.x_position = x_position

    def reset(self):
        """
        Reset the location to the origin

        """
        self.z_position = 0.
        self.y_position = 0.
        self.x_position = 0.
