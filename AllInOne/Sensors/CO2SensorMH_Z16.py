import smbus2
import time
import logging


logging.basicConfig(filename='parsing.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CO2Sensor():
    cmd_measure = [0xFF, 0x01, 0x9C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x63]
    ppm = 0

    IOCONTROL = 0x0E << 3
    FCR = 0x02 << 3
    LCR = 0x03 << 3
    DLL = 0x00 << 3
    DLH = 0x01 << 3
    THR = 0x00 << 3
    RHR = 0x00 << 3
    TXLVL = 0x08 << 3
    RXLVL = 0x09 << 3

    def __init__(self, i2c_addr=0x4D):
        self.i2c_addr = i2c_addr
        self.i2c = smbus2.SMBus(1)  # Create an I2C bus object

    def begin(self):
        try:
            self.write_register(self.IOCONTROL, 0x08)
        except IOError:
            pass
            
        self.write_register(self.FCR, 0x07)
        self.write_register(self.LCR, 0x83)
        self.write_register(self.DLL, 0x60)
        self.write_register(self.DLH, 0x00)
        self.write_register(self.LCR, 0x03)

    def getCO2(self):
        self.write_register(self.FCR, 0x07)
        self.send(self.cmd_measure)
        return self.parse(self.receive())

    def parse(self, response):
        checksum = 0

        if len(response) < 9:
            return 0

        for i in range(0, 9):
            checksum += response[i]

        if response[0] == 0xFF and response[1] == 0x9C and checksum % 256 == 0xFF:
            self.ppm = (response[2] << 24) + (response[3] << 16) + (response[4] << 8) + response[5]
            return self.ppm

    def read_register(self, reg_addr):
        time.sleep(0.02)
        return self.i2c.read_byte_data(self.i2c_addr, reg_addr)

    def write_register(self, reg_addr, val):
        time.sleep(0.001)
        self.i2c.write_byte_data(self.i2c_addr, reg_addr, val)

    def send(self, command):
        if self.read_register(self.TXLVL) >= len(command):
            self.i2c.write_i2c_block_data(self.i2c_addr, self.THR, command)

    def receive(self):
        n = 9
        buf = []
        start = time.time()
        
        while n > 0:
            time.sleep(0.001)
            rx_level = self.read_register(self.RXLVL)
            
            if rx_level > n:
                rx_level = n

            buf.extend(self.i2c.read_i2c_block_data(self.i2c_addr, self.RHR, rx_level))
            n = n - rx_level

            if time.time() - start > 0.2:
                break

        return buf

    def read_data(self):
        for i in range(3):
            try:
                self.begin()
                return self.getCO2()
            except Exception as e:
                logging.error(f"Error occurred during reading data from CO2 sensor: {str(e)}", exc_info=True)
                if i == 2:
                    return None
