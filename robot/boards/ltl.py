from serial import Serial
from struct import *
from math import pi
from threading import Thread

COMMAND_SETPIDPARAM = 0xA6
COMMAND_SETPOINT = 0xA7
COMMAND_GETSTATE = b'\xA8'
COMMAND_GETSTATE_RESPONSE = b'\xA9'
COMMAND_ENCODER_RESET = b'\xAA'
COMMAND_START_SAMPLING_SPEEDS = b'\xAB'
COMMAND_STOP_SAMPLING_SPEEDS = b'\xAC'


class Arduino(Thread):
    def __init__(self, port='/dev/ttyACM0', baudrate=9600, revolutionSteps=270.9, sampleTime=0.05):        
        Thread.__init__(self)
        self.serialPort = Serial(port, baudrate)
        self.batteryStatus = 100
        self.sampling = False
        self.speed1 = []
        self.speed2 = []
        self.pulses1 = 0
        self.pulses2 = 0
        self.lastPulses1 = 0
        self.lastPulses2 = 0
        self.setpoint1 = 0.0
        self.setpoint2 = 0.0
        self.pulsesFactor = 2.0 * pi / revolutionSteps / sampleTime
        self.daemon = True
        self.start()

    def read_state(self):
        self.serialPort.write(COMMAND_GETSTATE)
        header = self.serialPort.read()
        if header == COMMAND_GETSTATE_RESPONSE:
            pulses1 = self.serialPort.read()
            pulses1 += self.serialPort.read()
            pulses1 += self.serialPort.read()
            pulses1 += self.serialPort.read()
            pulses1, = unpack("i", pulses1)
                        
            pulses2 = self.serialPort.read()
            pulses2 += self.serialPort.read()
            pulses2 += self.serialPort.read()
            pulses2 += self.serialPort.read()
            pulses2, = unpack("i", pulses2)
            
            batteryCharge, = unpack('B', self.serialPort.read())
            
            self.lastPulses1 = self.pulses1
            self.lastPulses2 = self.pulses2
            self.pulses1= pulses1
            self.pulses2= pulses2
            self.batteryStatus = batteryCharge

        return self.pulses1, self.pulses2, self.batteryStatus

    def set_constants(self, kc, ki, kd):
        package = pack("<Bfff", COMMAND_SETPIDPARAM, kc, ki, kd)
        self.serialPort.write(package)


    def set_speeds(self, speed1, speed2):
        self.setpoint1 = speed1
        self.setpoint2 = speed2
        package = pack("<Bff", COMMAND_SETPOINT, speed1, speed2)
        self.serialPort.write(package)

    def reset_encoders(self):
        self.serialPort.write(COMMAND_ENCODER_RESET)

    def start_sampling_speeds(self):
        self.serialPort.write(COMMAND_START_SAMPLING_SPEEDS)        
        self.sampling = True

    def stop_sampling_speeds(self):
        self.serialPort.write(COMMAND_STOP_SAMPLING_SPEEDS)
        self.sampling = False

    def run(self):
        while True:
            if self.sampling == True:
                while self.serialPort.inWaiting() < 4:
                    pass
                speed1 = self.serialPort.read()
                speed1 += self.serialPort.read()
                speed1 += self.serialPort.read()
                speed1 += self.serialPort.read()
                speed1, = unpack("f", speed1)

                while self.serialPort.inWaiting() < 4:
                    pass
                speed2 = self.serialPort.read()
                speed2 += self.serialPort.read()
                speed2 += self.serialPort.read()
                speed2 += self.serialPort.read()
                speed2, = unpack("f", speed2)

                self.speed1.append(speed1)
                self.speed2.append(speed2) 

#TODO: Tirar el reset encoders y descomentar las lineas que lo usan