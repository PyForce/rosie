try:
    import smbus
except:
    print ("      Error importing SMBus")

"""
class Gyro:
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        self.bus.write_i2c_block_data(self.address, 0x20, [0x0F])
        self.bus.write_i2c_block_data(self.address, 0x21, [0x00])
        self.bus.write_i2c_block_data(self.address, 0x22, [0x08])
        self.bus.write_i2c_block_data(self.address, 0x23, [0x30])
        self.bus.write_i2c_block_data(self.address, 0x24, [0x00])

    def read_state(self):
        result0 = self.bus.read_i2c_block_data(self.address, 0x28, 1)
        result1 = self.bus.read_i2c_block_data(self.address, 0x29, 1)

        max_int_16 = 2 ** 15

        temp = (result0[0] * 0x100) + (result1[0])
        if temp > max_int_16:
            temp = -(2 ** 16 - temp)

        return (temp)
"""


class MD25:
    
    def __init__(self, bus, address):
        self.address = address
        try:
            self.bus = smbus.SMBus(bus)
        except:
            print ("      Error SMBus")

        self.reset_encoders()
        
        try:
            self.bus.write_byte_data(self.address, 15, 1)
            self.bus.write_byte_data(self.address, 16, 48)
            self.bus.write_byte_data(self.address, 14, 10)
        except:
            print ("      Error I2C")
        
        #--------------------------------
        self.set_speeds=self.drive_motors
        
    def drive_motors(self, motor1, motor2):
        try:           
            self.bus.write_i2c_block_data(self.address, 0, [motor2, motor1])
        except:
            print ("      Error I2C")

    def read_state(self):
        try:
            result = self.bus.read_i2c_block_data(self.address, 2, 11)
        except:
            print ("      Error I2C")
            return 0,0,0,0,0
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

        return encoder2, encoder1, battery_voltage, current_left, current_right

    def reset_encoders(self):
        try:
            self.bus.write_byte_data(self.address, 16, 32)
        except:
            print ("      Error I2C")

