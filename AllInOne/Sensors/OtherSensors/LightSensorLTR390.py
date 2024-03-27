"""
Description:
This module provides a class for interfacing with the LTR390 light sensor.

Dependencies:
    - time: Time-related functions.
    - board: CircuitPython board-specific functionality.
    - busio: Hardware communication library.
    - logger_config: Custom logging configuration.
    - config: Configuration settings for sensors.
    - Scripts.kalman: Kalman filter implementation.

Global Variables:
    - SENSORS: Configuration settings for sensors.

Classes:
    - LightSensor: A class for interacting with the LTR390 light sensor.
"""

import time
import board
import busio
from logger_config import *
from config import SENSORS
from Scripts.kalman import KalmanFilter
import adafruit_ltr390


class LightSensor:
    """
    A class for interfacing with the LTR390 light sensor.

    Attributes:
        working (bool): Indicates whether the sensor is operational.
        reading_time (int): Duration of data collection in seconds.
        testing (bool): Flag indicating whether the sensor is in test mode.
        i2c (busio.I2C): Instance of I2C bus communication.
        sensor (adafruit_ltr390.LTR390): Instance of LTR390 sensor.

    Methods:
        __init__: Initializes the LightSensor object.
        test_reading: Simulates sensor readings for testing purposes.
        read_data: Reads UV index and lux data from the sensor.
    """

    def __init__(self, testing=False) -> None:
        """
        Initializes the LightSensor object.

        Args:
            testing (bool, optional): Flag indicating whether the sensor is in test mode. Defaults to False.
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

    def test_reading(self):
        """
        Simulates sensor readings for testing purposes.

        Returns:
            dict: Dictionary containing simulated UV index and lux readings.
        """
        uvi = self.sensor.uvi
        lux = self.sensor.lux

        return {
            "uv": round(uvi, 2),
            "lux": round(lux, 2)
        }

    def read_data(self) -> dict:
        """
        Reads UV index and lux data from the sensor.

        Returns:
            dict: Dictionary containing UV index and lux readings.
        """
        if self.testing:
            return self.test_reading()

        if self.working:
            uv_filter = KalmanFilter()
            lux_filter = KalmanFilter()

            data_uv = []
            data_lux = []

            start_time = time.time()

            while time.time() - start_time <= self.reading_time:
                try:
                    uvi = self.sensor.uvi
                    lux = self.sensor.lux

                    data_uv.append(uv_filter.update(uvi))
                    data_lux.append(lux_filter.update(lux))

                    time.sleep(3)
                except Exception as e:
                    logging.error(f"Error occurred during reading data from LTR390 sensor: {str(e)}",
                                  exc_info=True)

            if len(data_uv) < 11 or len(data_lux) < 11:
                return {
                    "uv": None,
                    "lux": None
                }

            uv_value = sum(data_uv[10:]) / len(data_uv[10:])
            lux_value = sum(data_lux[10:]) / len(data_lux[10:])

            return {
                "uv": round(uv_value, 2),
                "lux": round(lux_value, 2)
            }
        else:
            return {
                "uv": None,
                "lux": None
            }
