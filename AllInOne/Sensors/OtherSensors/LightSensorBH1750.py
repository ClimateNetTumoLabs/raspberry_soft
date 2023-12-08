"""
    Module for interacting with a light sensor.

    This module provides a class, LightSensor, for reading light data from a specified sensor.

    Class Docstring:
    ----------------
    LightSensor:
        Interacts with a light sensor to read light data.

    Constructor:
        Initializes a LightSensor object based on the configuration specified in the SENSORS module.

    Class Attributes:
        working (bool): Indicates if the light sensor is operational.
        POWER_DOWN (int): Power down mode constant.
        POWER_ON (int): Power on mode constant.
        RESET (int): Reset mode constant.
        ONE_TIME_HIGH_RES_MODE_2 (int): One-time high-resolution mode constant.
        bus: (smbus2.SMBus): An instance of the SMBus for communication with the sensor.
        addr (int): I2C address of the sensor.
        mtreg (int): Sensitivity value for the sensor.
        mode (int): Mode of the sensor.

    Methods:
        _set_mode(self, mode): Set the mode of the sensor.
        power_down(self): Power down the sensor.
        power_on(self): Power on the sensor.
        reset(self): Reset the sensor.
        oneshot_high_res2(self): Trigger a one-shot high-resolution measurement.
        set_sensitivity(self, sensitivity=150): Set the sensitivity of the sensor.
        get_result(self): Get the result from the sensor.
        wait_for_result(self, additional=0): Wait for the sensor to provide a result.
        read_data(self, additional_delay=0): Read light data from the sensor, handling exceptions and returning the data.

    Module Usage:
    -------------
    To use this module, create an instance of the LightSensor class. Call the read_data() method to get light data.
"""

import smbus2
import time
from logger_config import *
from config import SENSORS


class LightSensor:
    """
    Interacts with a light sensor to read light data.

    Attributes:
        working (bool): Indicates if the light sensor is operational.
        POWER_DOWN (int): Power down mode constant.
        POWER_ON (int): Power on mode constant.
        RESET (int): Reset mode constant.
        ONE_TIME_HIGH_RES_MODE_2 (int): One-time high-resolution mode constant.
        bus: (smbus2.SMBus): An instance of the SMBus for communication with the sensor.
        addr (int): I2C address of the sensor.
        mtreg (int): Sensitivity value for the sensor.
        mode (int): Mode of the sensor.
    """
    def __init__(self, addr=0x23) -> None:
        """
        Initializes a LightSensor object based on the configuration specified in the SENSORS module.
        """
        sensor_info = SENSORS["light_sensor"]

        self.working = sensor_info["working"]

        if self.working:
            self.POWER_DOWN = 0x00
            self.POWER_ON = 0x01
            self.RESET = 0x07

            self.bus = smbus2.SMBus(1)
            self.addr = addr
            self.power_down()
            self.set_sensitivity()
            self.ONE_TIME_HIGH_RES_MODE_2 = 0x21

    def _set_mode(self, mode):
        self.mode = mode
        self.bus.write_byte(self.addr, self.mode)

    def power_down(self):
        self._set_mode(self.POWER_DOWN)

    def power_on(self):
        self._set_mode(self.POWER_ON)

    def reset(self):
        self.power_on()
        self._set_mode(self.RESET)

    def oneshot_high_res2(self):
        self._set_mode(self.ONE_TIME_HIGH_RES_MODE_2)

    def set_sensitivity(self, sensitivity=150):
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
        data = self.bus.read_word_data(self.addr, self.mode)
        count = data >> 8 | (data & 0xff) << 8
        mode2coeff = 2 if (self.mode & 0x03) == 0x01 else 1
        ratio = 1 / (1.2 * (self.mtreg / 69.0) * mode2coeff)
        return ratio * count

    def wait_for_result(self, additional=0):
        basetime = 0.018 if (self.mode & 0x03) == 0x03 else 0.128
        time.sleep(basetime * (self.mtreg / 69.0) + additional)

    def read_data(self, additional_delay=0) -> dict:
        """
        Read light data from the sensor, handling exceptions and returning the data.

        Args:
            additional_delay (int): Additional delay time in seconds.

        Returns:
            dict: A dictionary containing the light data. If an error occurs, returns a dictionary with None values.
        """
        if self.working:
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
                        logging.error(f"Error occurred during reading data from Light sensor: [Errno 121] Remote I/O "
                                      f"error")
                    else:
                        logging.error(f"Error occurred during reading data from Light sensor: {str(e)}", exc_info=True)
                    if i == 2:
                        return {
                            "light": None
                        }
        else:
            return {
                "light": None
            }
