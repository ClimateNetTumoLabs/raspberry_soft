import struct
import time

import RPi.GPIO as GPIO
import serial

__version__ = '0.0.5'

PMS5003_SOF = bytearray(b'\x42\x4d')


class ChecksumMismatchError(RuntimeError):
    pass


class ReadTimeoutError(RuntimeError):
    pass


class SerialTimeoutError(RuntimeError):
    pass


class PMS5003Data:
    """
    Represents data received from the PMS5003 sensor.
    """

    def __init__(self, raw_data):
        """
        Initialize PMS5003Data with raw data.

        Args:
            raw_data (bytes): Raw data received from the PMS5003 sensor.
        """
        self.raw_data = raw_data
        self.data = struct.unpack(">HHHHHHHHHHHHHH", raw_data)
        self.checksum = self.data[13]

    def pm_ug_per_m3(self, size, atmospheric_environment=False):
        """
        Get particulate matter (PM) concentration in ug/m3.

        Args:
            size (float): The size of PM (1.0, 2.5, or 10).
            atmospheric_environment (bool): True for atmospheric environment mode.

        Returns:
            int: PM concentration in ug/m3.
        """
        if atmospheric_environment:
            if size == 1.0:
                return self.data[3]
            if size == 2.5:
                return self.data[4]
            if size == 10:
                return self.data[5]

        else:
            if size == 1.0:
                return self.data[0]
            if size == 2.5:
                return self.data[1]
            if size == 10:
                return self.data[2]

    def pm_per_1l_air(self, size):
        """
        Get particulate matter (PM) concentration per 1L of air.

        Args:
            size (float): The size of PM (0.3, 0.5, 1.0, 2.5, 5, or 10).

        Returns:
            int: PM concentration per 1L of air.
        """
        if size == 0.3:
            return self.data[6]
        if size == 0.5:
            return self.data[7]
        if size == 1.0:
            return self.data[8]
        if size == 2.5:
            return self.data[9]
        if size == 5:
            return self.data[10]
        if size == 10:
            return self.data[11]

        raise ValueError("Particle size {} measurement not available.".format(size))


class PMS5003:
    """
    PMS5003 Sensor interface class.
    """

    def __init__(self,
                 device='/dev/ttyAMA0',
                 baudrate=9600,
                 pin_enable=22,
                 pin_reset=27,
                 pin_enable_working=True,
                 pin_reset_working=False):
        """
        Initialize PMS5003 sensor.

        Args:
            device (str): The serial device path (default is '/dev/ttyAMA0').
            baudrate (int): The baud rate for communication (default is 9600).
            pin_enable (int): The GPIO pin number for enabling the sensor (default is 22).
            pin_reset (int): The GPIO pin number for resetting the sensor (default is 27).
        """
        self._serial = None
        self._device = device
        self._baudrate = baudrate
        self._pin_enable = pin_enable
        self._pin_enable_working = pin_enable_working
        self._pin_reset = pin_reset
        self._pin_reset_working = pin_reset_working

        self.setup()

    def setup(self):
        """
        Setup the PMS5003 sensor.
        """
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        if self._pin_enable_working:
            GPIO.setup(self._pin_enable, GPIO.OUT, initial=GPIO.HIGH)
        if self._pin_reset_working:
            GPIO.setup(self._pin_reset, GPIO.OUT, initial=GPIO.HIGH)

        if self._serial is not None:
            self._serial.close()

        self._serial = serial.Serial(self._device, baudrate=self._baudrate, timeout=4)

        if self._pin_reset_working:
            self.reset()

    def stop(self):
        GPIO.output(self._pin_enable, GPIO.LOW)

    def reset(self):
        """
        Reset the PMS5003 sensor.
        """
        time.sleep(0.1)
        GPIO.output(self._pin_reset, GPIO.LOW)
        self._serial.flushInput()
        time.sleep(0.1)
        GPIO.output(self._pin_reset, GPIO.HIGH)

    def read(self):
        """
        Read data from the PMS5003 sensor.

        Returns:
            PMS5003Data: Object containing data read from the sensor.
        """
        start = time.time()

        sof_index = 0

        while True:
            elapsed = time.time() - start
            if elapsed > 5:
                raise ReadTimeoutError("PMS5003 Read Timeout: Could not find start of frame")

            sof = self._serial.read(1)
            if len(sof) == 0:
                raise SerialTimeoutError("PMS5003 Read Timeout: Failed to read start of frame byte")
            sof = ord(sof) if type(sof) is bytes else sof

            if sof == PMS5003_SOF[sof_index]:
                if sof_index == 0:
                    sof_index = 1
                elif sof_index == 1:
                    break
            else:
                sof_index = 0

        checksum = sum(PMS5003_SOF)

        data = bytearray(self._serial.read(2))
        if len(data) != 2:
            raise SerialTimeoutError("PMS5003 Read Timeout: Could not find length packet")
        checksum += sum(data)
        frame_length = struct.unpack(">H", data)[0]

        raw_data = bytearray(self._serial.read(frame_length))
        if len(raw_data) != frame_length:
            raise SerialTimeoutError("PMS5003 Read Timeout: Invalid frame length. Got {} bytes, expected {}."
                                     .format(len(raw_data), frame_length))

        data = PMS5003Data(raw_data)

        checksum += sum(raw_data[:-2])

        if checksum != data.checksum:
            raise ChecksumMismatchError("PMS5003 Checksum Mismatch {} != {}".format(checksum, data.checksum))

        return data
