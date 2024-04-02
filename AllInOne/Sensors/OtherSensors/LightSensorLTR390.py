"""
Description:
This module provides functionality for interfacing with the light sensor (LTR390).

Dependencies:
    - time: Time-related functions.
    - board: CircuitPython board module.
    - busio: CircuitPython module for bus communication.
    - Scripts.kalman_data_collector: Custom KalmanDataCollector class for filtering data.
    - logger_config: Logging configuration.
    - config: Configuration file containing sensors information.
    - adafruit_ltr390: Adafruit library for the LTR390 light sensor.

Global Variables:
    - None
"""

import time
import board
import busio
from Scripts.kalman_data_collector import KalmanDataCollector
from logger_config import *
from config import SENSORS
import adafruit_ltr390


class LightSensor:
    """
    A class to represent a Light Sensor.

    Attributes:
        working (bool): Indicates whether the sensor should be operational or not.
        reading_time (int): The duration for reading sensor data.
        testing (bool): Flag indicating if the sensor is in testing mode.
        i2c: Instance of the I2C bus for communication.
        sensor: Instance of the LTR390 light sensor.
    """

    def __init__(self, testing=False) -> None:
        """
        Initializes the LightSensor object.

        Args:
            testing (bool, optional): Flag to indicate testing mode. Defaults to False.
        """
        sensor_info = SENSORS["light_sensor"]
        self.working = sensor_info["working"]
        self.reading_time = sensor_info["reading_time"]
        self.testing = testing

        if self.working or self.testing:
            for i in range(3):
                try:
                    self.i2c = busio.I2C(board.SCL, board.SDA)
                    self.sensor = adafruit_ltr390.LTR390(self.i2c)
                    break
                except OSError or ValueError:
                    logging.error(
                        "Error occurred during creating object for LTR390 sensor: No I2C device at address")
                except Exception as e:
                    logging.error(f"Error occurred during creating object for LTR390 sensor: {str(e)}")

                if i == 2:
                    self.working = False

    def __get_data(self):
        """
        Private method to retrieve data from the light sensor.

        Returns:
            dict: A dictionary containing UV index and Lux values.
        """
        uvi = self.sensor.uvi
        lux = self.sensor.lux

        return {
            "uv": round(uvi, 2),
            "lux": round(lux, 2)
        }

    def read_data(self) -> dict:
        """
        Reads and optionally filters data from the light sensor.

        Returns:
            dict: A dictionary containing UV index and Lux values. If the sensor is in testing mode,
            returns unfiltered data. If operational, applies Kalman filtering to the data before returning.

        Raises:
            Exception: If any error occurs during the process, it's logged and None values are returned for UV and Lux.
        """
        if self.testing:
            return self.__get_data()
        elif self.working:
            kalman_data_collector = KalmanDataCollector('uv', 'lux')

            start_time = time.time()

            while time.time() - start_time <= self.reading_time:
                try:
                    data = self.__get_data()
                    kalman_data_collector.add_data(data)

                    time.sleep(3)
                except Exception as er:
                    logging.error(f"Error occurred during reading data from LTR390 sensor: {str(er)}",
                                  exc_info=True)

            return kalman_data_collector.get_result()

        else:
            return {
                "uv": None,
                "lux": None
            }
