import serial
import struct
import time
import sys


class SPS30:
    START_END_BYTE = 0x7E
    ADDRESS = 0x00
    START_MEASUREMENT = 0x00
    STOP_MEASUREMENT = 0x01
    READ_MEASURED_VALUE = 0x03
    SLEEP = 0x10
    WAKE_UP = 0x11
    START_FAN_CLEANING = 0x56
    AUTO_CLEANING_INTERVAL = 0x80
    RESET = 0xD3
    DEVICE_INFORMATION = 0xD0
    READ_VERSION = 0xD1
    READ_STATUS_REGISTER = 0xD2

    def __init__(self, port='/dev/ttyS0', baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)

    def calcCheckSum(self, dataBytes):
        total = sum(dataBytes)
        lsb = total & 0xFF
        checksum = (~lsb) & 0xFF
        return checksum

    def readFrame(self, max_len=255, command=None):
        buffer = bytearray()

        start_found = False

        start_time = time.time()
        while time.time() - start_time < self.ser.timeout:
            byte = self.ser.read(1)
            if not byte:
                continue

            b = byte[0]
            if b == self.START_END_BYTE:
                if not start_found:
                    start_found = True
                    buffer = bytearray()
                    buffer.append(b)
                else:
                    buffer.append(b)
                    break
            elif start_found:
                buffer.append(b)

        if not buffer:
            raise Exception("Frame is empty")

        if len(buffer) < 7:
            raise Exception("Frame too short or timed out")

        if buffer[0] != self.START_END_BYTE or buffer[-1] != self.START_END_BYTE:
            raise Exception(f"Invalid start/end byte: {buffer.hex()}")

        unstuffed = self.unstuff(buffer[1:-1])
        addr = unstuffed[0]
        cmd = unstuffed[1]
        state = unstuffed[2]
        length = unstuffed[3]
        data = unstuffed[4:4 + length]
        checksum = unstuffed[4 + length]
        calc_checksum = self.calcCheckSum(unstuffed[:4 + length])

        if cmd != command:
            raise Exception(f"Command mismatch: expected {command}, got {data[2]}")

        if state != 0:
            raise Exception(f"Device returned error state: {data[3]}")

        if checksum != calc_checksum:
            raise Exception(f"Checksum mismatch: got 0x{checksum:02X}, expected 0x{calc_checksum:02X}")

        return data

    def makeFrame(self, command, data=b''):
        frame_body = bytearray()
        frame_body.append(self.ADDRESS)
        frame_body.append(command)
        frame_body.append(len(data))
        frame_body.extend(data)

        checksum = self.calcCheckSum(frame_body)
        frame_body.append(checksum)

        stuffed = self.stuff(frame_body)

        frame = bytearray([self.START_END_BYTE]) + stuffed + bytearray([self.START_END_BYTE])
        return frame

    def sendCommand(self, command, data=b'', responseLen=0, delay=0.05):
        frame = self.makeFrame(command, data)
        self.ser.write(frame)
        time.sleep(delay)
        if responseLen > 0:
            return self.readFrame(responseLen, command)
        return b''

    def startMeasurement(self, format_type=0x03):
        data = bytes([0x01, format_type])
        self.sendCommand(self.START_MEASUREMENT, data)
        self.ser.reset_input_buffer()

    def stopMeasurement(self):
        self.sendCommand(self.STOP_MEASUREMENT)
        self.ser.reset_input_buffer()

    def getVersion(self):
        data = self.sendCommand(self.READ_VERSION, responseLen=14)
        return {
            "Firmware": f'{data[0]}.{data[1]}',
            "SHDLC": f'{data[5]}.{data[6]}'
        }

    def resetDevice(self):
        self.sendCommand(self.RESET)
        self.ser.reset_input_buffer()

    def sleepDevice(self):
        self.sendCommand(self.SLEEP)
        self.ser.reset_input_buffer()

    def wakeUpDevice(self):
        self.ser.write(b'\xFF')
        self.sendCommand(self.WAKE_UP)
        self.ser.reset_input_buffer()

    def startFanCleaning(self):
        print("Start Fan Cleanning...")
        self.sendCommand(self.START_FAN_CLEANING)
        self.ser.reset_input_buffer()
        for i in range(1, 101):
            time.sleep(0.1)
            sys.stdout.write(f"\rProgress: {i}%")
            sys.stdout.flush()
        time.sleep(0.1)
        print("\nFan Cleanning is done.")

    def readDeviceInfo(self):
        data = bytes([0x03])
        response = self.sendCommand(self.DEVICE_INFORMATION, data=data, responseLen=32)

        try:
            decoded = response.decode('ascii').strip('\x00')
            print(decoded)
        except UnicodeDecodeError:
            print("Response is not valid ASCII:", response)

        return {
            "Product Type": "00080000",
            "Serial": decoded
        }

    def stuff(self, data):
        stuffed = bytearray()
        for b in data:
            if b in [0x7E, 0x7D, 0x11, 0x13]:
                stuffed.append(0x7D)
                stuffed.append(b ^ 0x20)
            else:
                stuffed.append(b)
        return stuffed

    def unstuff(self, stuffed):
        i = 0
        unstuffed = bytearray()
        while i < len(stuffed):
            if stuffed[i] == 0x7D:
                i += 1
                if i >= len(stuffed):
                    raise ValueError("Invalid stuffing at end of frame")
                unstuffed.append(stuffed[i] ^ 0x20)
            else:
                unstuffed.append(stuffed[i])
            i += 1
        return unstuffed

    def readStatusRegister(self, reset=False):
        data = bytes([0x01]) if reset else bytes([0x00])
        response = self.sendCommand(self.READ_STATUS_REGISTER, data, responseLen=12)
        status_reg = struct.unpack(">I", response[:4])[0]

        speed_bit = (status_reg >> 21) & 1
        laser_bit = (status_reg >> 5) & 1
        fan_bit = (status_reg >> 4) & 1

        return {
            "Speed": speed_bit,
            "Laser": laser_bit,
            "Fan": fan_bit
        }

    def readMeasurement(self):
        self.sendCommand(self.READ_MEASURED_VALUE)
        time.sleep(1.0)
        raw_data = self.readFrame(command=self.READ_MEASURED_VALUE)

        if len(raw_data) != 40:
            raise Exception(f"Expected 40 bytes, got {len(raw_data)}")

        values = [struct.unpack(">f", raw_data[i:i + 4])[0] for i in range(0, 40, 4)]
        labels = [
            "Mass PM1.0",
            "Mass PM2.5",
            "Mass PM4.0",
            "Mass PM10",
            "Number PM0.5",
            "Number PM1.0",
            "Number PM2.5",
            "Number PM4.0",
            "Number PM10",
            "Particle Size"
        ]
        return dict(zip(labels, values))

    def readAutoCleaningInterval(self):
        data = bytes([0x00])  # Subcommand for reading
        response = self.sendCommand(self.AUTO_CLEANING_INTERVAL, data=data, responseLen=8)

        if len(response) != 4:
            raise Exception(f"Expected 4 bytes for interval, got {len(response)}: {response.hex()}")

        interval = struct.unpack(">I", response)[0]
        return interval

    def setAutoCleaningInterval(self, interval_seconds):
        if not (0 <= interval_seconds <= 0xFFFFFFFF):
            raise ValueError("Interval must be between 0 and 2^32-1 seconds")
        data = bytes([0x00]) + struct.pack(">I", interval_seconds)
        self.sendCommand(self.AUTO_CLEANING_INTERVAL, data)


    def stop(self):
        self.ser.close()
