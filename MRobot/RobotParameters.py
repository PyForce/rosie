__author__ = 'Silvio'


class DifferentialDriveRobotParameters:
    """
    Structure containing parameters for a differential drive mobile robot

    @param wheel_radius: Radius of the wheels
    @param wheel_distance: Distance between wheels
    @param steps_per_revolution: Encoders counts for a complete revolution of the wheels
    @param constant_b: Distance of the P point when using IOLinearization Controller
    @param constant_k1: Gain for X axis when using IO Linearization Controller
    @param constant_k2: Gain for Y axis when using IO Linearization Controller
    @param constant_ki: Integrative gain using PID Controller for the speeds
    @param constant_kd: Derivative gain using PID Controller for the speeds
    @param constant_kc: Proportional gain using PID Controller for the speeds
    @param max_value_power: Maximum value of the power to be driven to motors
    @param min_value_power: Minimum value of the power to be driven to motors
    @param sample_time: Sample time for the control system

    @type constant_kc: float
    @type constant_kd: float
    @type constant_ki: float
    @type constant_k2: float
    @type constant_k1: float
    @type constant_b: float
    @type steps_per_revolution: float
    @type wheel_distance: float
    @type wheel_radius: float
    @type max_value_power: float
    @type min_value_power: float
    @type sample_time: float
    """

    def __init__(self, wheel_radius, wheel_distance, steps_per_revolution, constant_b, constant_k1, constant_k2,
                 constant_ki, constant_kd, constant_kc, max_value_power, min_value_power, sample_time):
        self.sample_time = sample_time
        self.max_value_power = max_value_power
        self.min_value_power = min_value_power
        self.constant_kc = constant_kc
        self.constant_kd = constant_kd
        self.constant_ki = constant_ki
        self.constant_k2 = constant_k2
        self.constant_k1 = constant_k1
        self.constant_b = constant_b
        self.steps_per_revolution = steps_per_revolution
        self.wheel_distance = wheel_distance
        self.wheel_radius = wheel_radius
