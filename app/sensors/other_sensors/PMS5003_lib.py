import struct
import time

import RPi.GPIO as GPIO
import serial

__version__ = '0.0.5'

PMS5003_SOF = bytearray(b'\x42\x4d')


class ChecksumMismatchError(RuntimeError):
    """Exception raised for checksum mismatch errors in PMS5003 communication."""
    pass


class ReadTimeoutError(RuntimeError):
    """Exception raised for read timeout errors in PMS5003 communication."""
    pass


class SerialTimeoutError(RuntimeError):
    """Exception raised for serial timeout errors in PMS5003 communication."""
    pass


class PMS5003Data:
    """
    Class representing parsed data from PMS5003 sensor.

    Attributes:
        raw_data (bytes): Raw data received from the sensor.
        data (tuple): Parsed data as unpacked from raw_data.
        checksum (int): Calculated checksum value.
    """

    def __init__(self, raw_data: bytes):
        """
        Initializes PMS5003Data with raw data and unpacks it.

        Args:
            raw_data (bytes): Raw data received from PMS5003 sensor.
        """
        self.raw_data = raw_data
        self.data = struct.unpack(">HHHHHHHHHHHHHH", raw_data)
        self.checksum = self.data[13]

    def pm_ug_per_m3(self, size: float, atmospheric_environment: bool = False) -> int:
        """
        Retrieves particulate matter concentration in µg/m³.

        Args:
            size (float): Size of particulate matter (1.0, 2.5, 10).
            atmospheric_environment (bool, optional): Whether to get atmospheric environment data.

        Returns:
            int: Concentration of particulate matter in µg/m³.
        """
        if atmospheric_environment:
            if size == 1.0:
                return self.data[3]
            elif size == 2.5:
                return self.data[4]
            elif size == 10:
                return self.data[5]
        else:
            if size == 1.0:
                return self.data[0]
            elif size == 2.5:
                return self.data[1]
            elif size == 10:
                return self.data[2]

        raise ValueError(f"Particle size {size} measurement not available.")

    def pm_per_1l_air(self, size: float) -> int:
        """
        Retrieves particulate matter concentration per liter of air.

        Args:
            size (float): Size of particulate matter (0.3, 0.5, 1.0, 2.5, 5, 10).

        Returns:
            int: Concentration of particulate matter per liter of air.
        """
        if size == 0.3:
            return self.data[6]
        elif size == 0.5:
            return self.data[7]
        elif size == 1.0:
            return self.data[8]
        elif size == 2.5:
            return self.data[9]
        elif size == 5:
            return self.data[10]
        elif size == 10:
            return self.data[11]

        raise ValueError(f"Particle size {size} measurement not available.")


class PMS5003:
    """
    Class for interacting with the Plantower PMS5003 particulate matter sensor.

    Attributes:
        _serial (serial.Serial or None): Serial connection to the sensor.
        _device (str): Device path for the serial interface.
        _baudrate (int): Baud rate for serial communication.
        _pin_enable (int): GPIO pin number for enabling the sensor.
        _pin_enable_working (bool): Indicates if GPIO pin for enabling is active.
        _pin_reset (int): GPIO pin number for resetting the sensor.
        _pin_reset_working (bool): Indicates if GPIO pin for resetting is active.
    """

    def __init__(self,
                 device: str = '/dev/ttyAMA0',
                 baudrate: int = 9600,
                 pin_enable: int = 22,
                 pin_reset: int = 27,
                 pin_enable_working: bool = True,
                 pin_reset_working: bool = False):
        """
        Initializes the PMS5003 sensor instance.

        Args:
            device (str, optional): Device path for the serial interface.
            baudrate (int, optional): Baud rate for serial communication.
            pin_enable (int, optional): GPIO pin number for enabling the sensor.
            pin_reset (int, optional): GPIO pin number for resetting the sensor.
            pin_enable_working (bool, optional): Indicates if GPIO pin for enabling is active.
            pin_reset_working (bool, optional): Indicates if GPIO pin for resetting is active.
        """
        self._serial = None
        self._device = device
        self._baudrate = baudrate
        self._pin_enable = pin_enable
        self._pin_enable_working = pin_enable_working
        self._pin_reset = pin_reset
        self._pin_reset_working = pin_reset_working

        self.setup()

    def setup(self) -> None:
        """
        Sets up the serial connection and GPIO pins for the sensor.
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

    def stop(self) -> None:
        """
        Stops the sensor by setting the enable pin low.
        """
        GPIO.output(self._pin_enable, GPIO.LOW)

    def get_pin_state(self) -> str:
        """
        Retrieves the state of the enable pin.

        Returns:
            str: State of the enable pin ('HIGH' or 'LOW').
        """
        state = GPIO.input(self._pin_enable)
        return 'HIGH' if state == GPIO.HIGH else 'LOW'

    def reset(self) -> None:
        """
        Resets the sensor by toggling the reset pin.
        """
        time.sleep(0.1)
        GPIO.output(self._pin_reset, GPIO.LOW)
        self._serial.flushInput()
        time.sleep(0.1)
        GPIO.output(self._pin_reset, GPIO.HIGH)

    def read(self) -> PMS5003Data:
        """
        Reads data from the PMS5003 sensor.

        Returns:
            PMS5003Data: Parsed data object containing sensor readings.

        Raises:
            ReadTimeoutError: If reading times out.
            SerialTimeoutError: If serial communication times out.
            ChecksumMismatchError: If checksum verification fails.
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
            sof = ord(sof) if isinstance(sof, bytes) else sof

            if sof == PMS5003_SOF[sof_index]:
                if sof_index == 0:
                    sof_index = 1
                elif sof_index == 1:
                    break
            else:
                sof_index = 0

        checksum = sum(PMS5003_SOF)

        data_length_bytes = bytearray(self._serial.read(2))
        if len(data_length_bytes) != 2:
            raise SerialTimeoutError("PMS5003 Read Timeout: Could not find length packet")
        checksum += sum(data_length_bytes)
        frame_length = struct.unpack(">H", data_length_bytes)[0]

        raw_data = bytearray(self._serial.read(frame_length))
        if len(raw_data) != frame_length:
            raise SerialTimeoutError("PMS5003 Read Timeout: Invalid frame length. Got {} bytes, expected {}."
                                     .format(len(raw_data), frame_length))

        data = PMS5003Data(raw_data)

        checksum += sum(raw_data[:-2])

        if checksum != data.checksum:
            raise ChecksumMismatchError("PMS5003 Checksum Mismatch {} != {}".format(checksum, data.checksum))

        return data
