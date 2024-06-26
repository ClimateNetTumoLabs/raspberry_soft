"""
Description:
This module provides functionality for interfacing with the Air Quality sensor (PMS5003).

Dependencies:
    - time: Time-related functions.
    - .PMS5003_library: Custom library for the PMS5003 sensor.
    - logger_config: Logging configuration.
    - config: Configuration file containing sensors information.
    - scripts.kalman_data_collector: Custom KalmanDataCollector class for filtering data.

Global Variables:
    - None
"""

import time

from config import SENSORS
from logger_config import logging
from scripts.kalman_data_collector import KalmanDataCollector
from serial.serialutil import SerialException

from .PMS5003_lib import PMS5003, SerialTimeoutError, ReadTimeoutError, ChecksumMismatchError


class AirQualitySensor:
    """
    A class to represent an Air Quality Sensor.

    Attributes:
        working (bool): Indicates whether the sensor should be operational or not.
        reading_time (int): The duration for reading sensor data.
        testing (bool): Flag indicating if the sensor is in testing mode.
        pms5003: Instance of the PMS5003 sensor.
    """

    def __init__(self, testing=False) -> None:
        """
        Initializes the AirQualitySensor object.

        Args:
            testing (bool, optional): Flag to indicate testing mode. Defaults to False.
        """
        sensor_info = SENSORS["air_quality_sensor"]

        self.working = sensor_info["working"]
        self.reading_time = sensor_info["reading_time"]
        self.testing = testing

        if self.working or self.testing:
            for i in range(3):
                try:
                    self.pms5003 = PMS5003(
                        device=sensor_info["address"],
                        baudrate=sensor_info["baudrate"],
                        pin_enable=sensor_info["pin_enable"],
                        pin_reset=sensor_info["pin_reset"]
                    )
                    break
                except Exception as e:
                    logging.error(f"Error occurred during creating object for PMS5003 sensor: {e}")

                if i == 2:
                    self.working = False

    def __get_data(self) -> dict:
        """
        Private method to retrieve data from the Air Quality sensor.

        Returns:
            dict: A dictionary containing PM1, PM2.5, and PM10 values in micrograms per cubic meter (µg/m³).
        """
        self.pms5003.setup()
        data = {}

        try:
            all_data = self.pms5003.read()
        except SerialTimeoutError as e:
            logging.error(f"SerialTimeout error while reading PMS5003: {e}")
        except ReadTimeoutError as e:
            logging.error(f"ReadTimeout error while reading PMS5003: {e}")
        except SerialException as e:
            logging.error(f"SerialException error while reading PMS5003: {e}")
        except ChecksumMismatchError as e:
            logging.error(f"ChecksumMismatch error while reading PMS5003: {e}")
        except Exception as e:
            logging.error(f"Unhandled exception while reading PMS5003: {e}", exc_info=True)
        else:
            data["pm1"] = all_data.pm_ug_per_m3(size=1.0)
            data["pm2_5"] = all_data.pm_ug_per_m3(size=2.5)
            data["pm10"] = all_data.pm_ug_per_m3(size=10)

        return data

    def read_data(self) -> dict:
        """
        Reads data from the Air Quality sensor.

        Returns:
            dict: A dictionary containing PM1, PM2.5, and PM10 values in micrograms per cubic meter (µg/m³).
            If the sensor is in testing mode, returns raw data. If operational, applies Kalman filtering to the data
            before returning.

        Raises:
            Exception: If any error occurs during the process, it's logged and None values are returned for PM1, PM2.5,
            and PM10.
        """
        if self.testing:
            return self.__get_data()
        elif self.working:
            kalman_data_collector = KalmanDataCollector('pm1', 'pm2_5', 'pm10')

            start_time = time.time()

            while time.time() - start_time < self.reading_time:
                data = self.__get_data()
                if data:
                    kalman_data_collector.add_data(data)
                    time.sleep(2)
                time.sleep(1)

            return kalman_data_collector.get_result()

        return {"pm1": None, "pm2_5": None, "pm10": None}
