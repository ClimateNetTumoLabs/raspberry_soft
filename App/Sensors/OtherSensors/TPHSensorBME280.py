"""
Description:
This module provides functionality for interfacing with the TPH (Temperature, Pressure, Humidity) sensor (BME280).

Dependencies:
    - time: Time-related functions.
    - smbus2: Python3 support library for I2C access.
    - bme280: Library for the BME280 sensor.
    - Scripts.kalman_data_collector: Custom KalmanDataCollector class for filtering data.
    - logger_config: Logging configuration.
    - config: Configuration file containing sensors information.

Global Variables:
    - None
"""

import time
import smbus2
import bme280
from Scripts.kalman_data_collector import KalmanDataCollector
from logger_config import *
from config import SENSORS


class TPHSensor:
    """
    A class to represent a TPH (Temperature, Pressure, Humidity) Sensor.

    Attributes:
        port (int): The I2C port number.
        address (int): The I2C address of the sensor.
        testing (bool): Flag to indicate testing mode.
        working (bool): Indicates whether the sensor should be operational or not.
        reading_time (int): The duration for reading sensor data.
        bus: Instance of the I2C bus for communication.
        calibration_params: Calibration parameters for the sensor.
    """

    def __init__(self, port=1, address=0x76, testing=False):
        """
        Initializes the TPHSensor object.

        Args:
            port (int, optional): The I2C port number. Defaults to 1.
            address (int, optional): The I2C address of the sensor. Defaults to 0x76.
            testing (bool, optional): Flag to indicate testing mode. Defaults to False.
        """
        sensor_info = SENSORS["tph_sensor"]
        self.testing = testing
        self.working = sensor_info["working"]
        self.reading_time = sensor_info['reading_time']

        if self.working or self.testing:
            for i in range(3):
                try:
                    self.port = port
                    self.address = address
                    self.bus = smbus2.SMBus(self.port)
                    self.calibration_params = bme280.load_calibration_params(self.bus, self.address)
                    break
                except OSError:
                    logging.error("Error occurred during creating object for BME280 sensor: [Errno 5] Input/output "
                                  "error")
                except Exception as e:
                    logging.error(f"Error occurred during creating object for BME280 sensor: {str(e)}", exc_info=True)

                if i == 2:
                    self.working = False

    def __get_data(self):
        """
        Private method to retrieve data from the TPH sensor.

        Returns:
            dict: A dictionary containing temperature, pressure, and humidity values.
        """
        data = bme280.sample(self.bus, self.address, self.calibration_params)

        return {
            "temperature": round(data.temperature, 2),
            "pressure": round(data.pressure * 0.750061, 2),
            "humidity": round(data.humidity, 2)
        }

    def read_data(self) -> dict:
        """
        Reads data from the TPH sensor.

        Returns:
            dict: A dictionary containing temperature, pressure, and humidity values. If the sensor is in testing mode,
            returns unfiltered data. If operational, applies Kalman filtering to the data before returning.

        Raises:
            Exception: If any error occurs during the process, it's logged and None values are returned for temperature,
            pressure, and humidity.
        """
        if self.testing:
            return self.__get_data()
        elif self.working:
            kalman_data_collector = KalmanDataCollector('temperature', 'pressure', 'humidity')

            start_time = time.time()

            while time.time() - start_time <= self.reading_time:
                try:
                    data = self.__get_data()
                    kalman_data_collector.add_data(data)

                    time.sleep(3)
                except Exception as er:
                    logging.error(f"Error occurred during reading data from BME280 sensor: {str(er)}",
                                  exc_info=True)

            return kalman_data_collector.get_result()
        else:
            return {
                "temperature": None,
                "pressure": None,
                "humidity": None
            }
