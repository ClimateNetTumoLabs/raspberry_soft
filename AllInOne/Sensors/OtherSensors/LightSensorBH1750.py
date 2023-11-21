import smbus2
import time
from logger_config import *

class LightSensor:
    """
    Class for reading light intensity using a light sensor.

    This class provides methods for reading light intensity from a light sensor using the I2C protocol.

    Args:
        addr (int): The I2C address of the light sensor (default is 0x23).

    Attributes:
        POWER_DOWN (int): Power-down mode value.
        POWER_ON (int): Power-on mode value.
        RESET (int): Reset mode value.
        bus (SMBus2.SMBus): The I2C bus for communication.
        addr (int): The I2C address of the light sensor.
        mode: The current mode of the light sensor.
        ONE_TIME_HIGH_RES_MODE_2 (int): Mode for one-time high-resolution measurement.

    Methods:
        power_down(self):
            Set the light sensor to power-down mode.

        power_on(self):
            Set the light sensor to power-on mode.

        reset(self):
            Reset the light sensor to initial state.

        oneshot_high_res2(self):
            Perform a one-time high-resolution measurement.

        set_sensitivity(self, sensitivity=150):
            Set the sensitivity of the light sensor.

        get_result(self):
            Read and return the measurement result from the light sensor.

        wait_for_result(self, additional=0):
            Wait for the measurement result to be ready.

        read_data(self, additional_delay=0):
            Attempt to read light intensity data multiple times, handling exceptions and returning the data.

    """

    def __init__(self, read, addr=0x23):
        """
        Initialize the LightSensor class.

        This method initializes the LightSensor class and sets up the I2C bus, the address of the light sensor,
        and initial modes.

        Args:
            addr (int): The I2C address of the light sensor (default is 0x23).

        Returns:
            None
        """
        
        self.read = read

        if self.read:
            self.POWER_DOWN = 0x00
            self.POWER_ON = 0x01
            self.RESET = 0x07

            self.bus = smbus2.SMBus(1)
            self.addr = addr
            self.power_down()
            self.set_sensitivity()
            self.ONE_TIME_HIGH_RES_MODE_2 = 0x21
        

    def _set_mode(self, mode):
        """
        Set the mode of the light sensor.

        Args:
            mode (int): The mode value to set.

        Returns:
            None
        """
        self.mode = mode
        self.bus.write_byte(self.addr, self.mode)

    def power_down(self):
        """
        Set the light sensor to power-down mode.

        This method sets the light sensor to power-down mode.

        Returns:
            None
        """
        self._set_mode(self.POWER_DOWN)

    def power_on(self):
        """
        Set the light sensor to power-on mode.

        This method sets the light sensor to power-on mode.

        Returns:
            None
        """
        self._set_mode(self.POWER_ON)

    def reset(self):
        """
        Reset the light sensor to initial state.

        This method resets the light sensor to its initial state by powering it on and setting it to reset mode.

        Returns:
            None
        """
        self.power_on()
        self._set_mode(self.RESET)

    def oneshot_high_res2(self):
        """
        Perform a one-time high-resolution measurement.

        This method configures the light sensor to perform a one-time high-resolution measurement.

        Returns:
            None
        """
        self._set_mode(self.ONE_TIME_HIGH_RES_MODE_2)

    def set_sensitivity(self, sensitivity=150):
        """
        Set the sensitivity of the light sensor.

        This method sets the sensitivity of the light sensor, taking into account the provided sensitivity value.

        Args:
            sensitivity (int): The sensitivity value to set (default is 150).

        Returns:
            None
        """
        if sensitivity < 31:
            self.mtreg = 31
        elif sensitivity > 254:
            self.mtreg = 254
        else:
            self.mtreg = sensitivity
        self.power_on()
        self._set_mode(0x40 | (self.mtreg >> 5))
        self._set_mode(0x60 | (self.mtreg & 0x1f))
        self.power_down()

    def get_result(self):
        """
        Read and return the measurement result from the light sensor.

        This method reads the measurement result from the light sensor and returns the result as a floating-point value.

        Returns:
            float: The measured light intensity.

        """
        data = self.bus.read_word_data(self.addr, self.mode)
        count = data >> 8 | (data & 0xff) << 8
        mode2coeff = 2 if (self.mode & 0x03) == 0x01 else 1
        ratio = 1 / (1.2 * (self.mtreg / 69.0) * mode2coeff)
        return ratio * count

    def wait_for_result(self, additional=0):
        """
        Wait for the measurement result to be ready.

        This method waits for the measurement result to be ready, taking into account the sensor's mode and sensitivity.

        Args:
            additional (float): Additional delay time (default is 0).

        Returns:
            None
        """
        basetime = 0.018 if (self.mode & 0x03) == 0x03 else 0.128
        time.sleep(basetime * (self.mtreg / 69.0) + additional)

    def read_data(self, additional_delay=0):
        """
        Attempt to read light intensity data multiple times, handling exceptions and returning the data.

        This method attempts to read light intensity data multiple times, handling exceptions that may occur
        during the reading process. It returns the light intensity data as a floating-point value or None in case of an error.

        Args:
            additional_delay (float): Additional delay time (default is 0).

        Returns:
            float or None: The measured light intensity, or None in case of an error.
        """
        if self.read:
            for i in range(3):
                try:
                    self.reset()
                    self._set_mode(self.ONE_TIME_HIGH_RES_MODE_2)
                    self.wait_for_result(additional=additional_delay)
                    return {
                        "light": round(self.get_result(), 2)
                    }
                except Exception as e:
                    if isinstance(e, OSError):
                        logging.error(f"Error occurred during reading data from Light sensor: [Errno 121] Remote I/O error")
                    else:
                        logging.error(f"Error occurred during reading data from Light sensor: {str(e)}", exc_info=True)
                    if i == 2:
                        return None
        else:
            return {
                "light": None
            }
