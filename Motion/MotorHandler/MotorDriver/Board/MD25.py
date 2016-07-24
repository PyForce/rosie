import smbus
from Motion.MotorHandler.MotorDriver.Dual import DualPowerMotorDriver

__author__ = 'Silvio'


class MD25MotorDriver(DualPowerMotorDriver):
    """
    Class to use MD25 motor controller board using I2C bus

    @param i2c_bus_number: I2C bus number to use
    @param i2c_bus_address:  I2C bus address of the MD25 board
    @type i2c_bus_address: int
    @type i2c_bus_number: int
    """
    MAX_ENCODER_COUNT_DELTA = 180
    MAX_ENCODER_COUNT = 2000000000

    def __init__(self, i2c_bus_number, i2c_bus_address):
        super(MD25MotorDriver, self).__init__()
        self.prev_encoder_count_1 = 0
        self.prev_encoder_count_2 = 0
        self.encoder_count_1 = 0
        self.encoder_count_2 = 0
        self.prev_delta_encoder_count_1 = 0
        self.prev_delta_encoder_count_2 = 0

        self.i2c_bus_address = i2c_bus_address
        self.i2c_bus = smbus.SMBus(i2c_bus_number)

        self.reset_encoders()
        self.i2c_bus.write_byte_data(self.i2c_bus_address, 15, 1)
        self.i2c_bus.write_byte_data(self.i2c_bus_address, 16, 48)
        self.i2c_bus.write_byte_data(self.i2c_bus_address, 14, 10)

    def set_powers(self, power_1, power_2):
        """
        Method to set the power for each motor

        @type power_2: float
        @type power_1: float
        @param power_1: Power for motor 1
        @param power_2: Power for motor 2
        """
        self.i2c_bus.write_i2c_block_data(self.i2c_bus_address, 0, [int(power_1), int(power_2)])

    def read_delta_encoders_count_state(self):
        """
        Reads the encoders count since last read and state of the motors

        @rtype : tuple
        @return: encoders count since last read (2 integers), battery voltage (float), motor's current (2 floats)
        """
        encoder_count_1, encoder_count_2, battery_voltage, current_left, current_right = self.read_state()

        delta_encoder_count_1 = encoder_count_1 - self.prev_encoder_count_1
        delta_encoder_count_2 = encoder_count_2 - self.prev_encoder_count_2

        self.encoder_count_1 = encoder_count_1
        self.encoder_count_2 = encoder_count_2

        if delta_encoder_count_1 > MD25MotorDriver.MAX_ENCODER_COUNT_DELTA \
                or delta_encoder_count_1 < -MD25MotorDriver.MAX_ENCODER_COUNT_DELTA:
            temp = delta_encoder_count_1
            delta_encoder_count_1 = self.prev_delta_encoder_count_1
            self.encoder_count_1 = 0
            self.encoder_count_2 = 0
            self.reset_encoders()
            print "delta_encoder_count_1 > MD25MotorDriver.MAX_ENCODER_COUNT_DELTA"
            print delta_encoder_count_1, temp

        if delta_encoder_count_2 > MD25MotorDriver.MAX_ENCODER_COUNT_DELTA \
                or delta_encoder_count_2 < -MD25MotorDriver.MAX_ENCODER_COUNT_DELTA:
            temp = delta_encoder_count_2
            delta_encoder_count_2 = self.prev_delta_encoder_count_2
            self.encoder_count_1 = 0
            self.encoder_count_2 = 0
            self.reset_encoders()
            print "delta_encoder_count_2 > MD25MotorDriver.MAX_ENCODER_COUNT_DELTA"
            print delta_encoder_count_2, temp

        if encoder_count_1 > MD25MotorDriver.MAX_ENCODER_COUNT \
                or encoder_count_1 < -MD25MotorDriver.MAX_ENCODER_COUNT \
                or encoder_count_2 > MD25MotorDriver.MAX_ENCODER_COUNT \
                or encoder_count_2 < -MD25MotorDriver.MAX_ENCODER_COUNT:
            self.encoder_count_1 = 0
            self.encoder_count_2 = 0
            self.reset_encoders()
            print "MD25MotorDriver.MAX_ENCODER_COUNT"

        self.prev_encoder_count_1 = self.encoder_count_1
        self.prev_encoder_count_2 = self.encoder_count_2

        self.prev_delta_encoder_count_1 = delta_encoder_count_1
        self.prev_delta_encoder_count_2 = delta_encoder_count_2

        return delta_encoder_count_1, delta_encoder_count_2, battery_voltage, current_left, current_right

    def reset(self):
        """
        Reset the driver

        """
        self.prev_encoder_count_1 = 0
        self.prev_encoder_count_2 = 0
        self.encoder_count_1 = 0
        self.encoder_count_2 = 0
        self.prev_delta_encoder_count_1 = 0
        self.prev_delta_encoder_count_2 = 0
        self.reset_encoders()

    def reset_encoders(self):
        """
        Private method to reset the encoders count of the MD25 board

        """
        self.i2c_bus.write_byte_data(self.i2c_bus_address, 16, 32)

    def read_state(self):
        """
        Private method to read the state of the MD25 board

        @rtype : tuple
        @return : both motors' encoders count (2 int), battery's voltage (float), both motors' current (2 float)
        """
        result = self.i2c_bus.read_i2c_block_data(self.i2c_bus_address, 2, 11)
        max_int_32 = 2 ** 31

        encoder1 = (result[0] << 24) + (result[1] << 16) + \
                   (result[2] << 8) + result[3]
        if encoder1 > max_int_32:
            encoder1 = -(2 ** 32 - encoder1)

        encoder2 = (result[4] << 24) + (result[5] << 16) + \
                   (result[6] << 8) + result[7]
        if encoder2 > max_int_32:
            encoder2 = -(2 ** 32 - encoder2)

        battery_voltage = result[8] / float(10)
        current_left = result[9] / float(10)
        current_right = result[10] / float(10)

        return encoder1, encoder2, battery_voltage, current_left, current_right
