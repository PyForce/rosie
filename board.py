import smbus


class MD25:
    """
    Class to handle MD25 board through I2C bus

    @param bus: The I2C bus to be used
    @param address: The address of the MD25 board on the I2c bus
    @type address: int
    @type bus: int
    """

    def __init__(self, bus, address):
        """
        Constructor of the class to handle MD25 board through I2C bus

        @param bus: The I2C bus to be used
        @param address: The address of the MD25 board on the I2c bus
        @type address: int
        @type bus: int
        """
        self.address = address
        self.bus = smbus.SMBus(bus)

        self.reset_encoders()
        self.bus.write_byte_data(self.address, 15, 1)
        self.bus.write_byte_data(self.address, 16, 48)
        self.bus.write_byte_data(self.address, 14, 10)

    def drive_motors(self, motor1, motor2):
        """
        Drive the specified powers to both motors

        @type motor2: int
        @type motor1: int
        @param motor1: Power to be driven to motor 1
        @param motor2: Power to be driven to motor 2
        """
        self.bus.write_i2c_block_data(self.address, 0, [motor1, motor2])

    def read_state(self):
        """
        Read the state of the MD25 board

        @rtype : tuple
        @return: encoder's count of motor 1, encoder's count of motor 2, voltage of the battery, current in motor 1, current in motor 2
        """
        result = self.bus.read_i2c_block_data(self.address, 2, 11)
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

    def reset_encoders(self):
        """
        Reset the encoder's count for both motors

        """
        self.bus.write_byte_data(self.address, 16, 32)
