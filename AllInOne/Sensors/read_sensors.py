"""
    Module for reading data from various sensors.

    This module provides a ReadSensors class for collecting data from a set of sensors.

    Class Docstring:
    ----------------
    ReadSensors:
        Reads data from different sensors including light, temperature, pressure, humidity, air quality, wind direction, wind speed, and rain.

    Constructor:
        Initializes a ReadSensors object with instances of various sensor classes.

    Class Attributes:
        sensors (list): List of sensor instances including LightSensor, TPHSensor, and AirQualitySensor.
        wind_direction_sensor (WindDirection): Instance of WindDirection class for reading wind direction data.
        wind_speed_sensor (WindSpeed): Instance of WindSpeed class for reading wind speed data.
        rain_sensor (Rain): Instance of Rain class for reading rain data.

    Methods:
        __get_data(self, start_time): Private method to collect data from sensors and calculate wind direction and speed.
        collect_data(self): Public method to collect data from sensors including wind direction and speed.

    Module Usage:
    -------------
    To use this module, create an instance of the ReadSensors class. Call collect_data() to obtain a dictionary containing data from various sensors.

"""

import time
from .WeatherMeterSensors import *
from .OtherSensors import *
from logger_config import *
import config


class ReadSensors:
    """
    Reads data from different sensors including light, temperature, pressure, humidity, air quality, wind direction, wind speed, and rain.
    """
    def __init__(self) -> None:
        """
        Initializes a ReadSensors object with instances of various sensor classes.
        """
        self.sensors = [
            LightSensor(),
            TPHSensor(),
            AirQualitySensor()
        ]

        self.wind_direction_sensor = WindDirection()
        self.wind_speed_sensor = WindSpeed()
        self.rain_sensor = Rain()

        if config.SENSORS["wind_speed"]["working"]:
            self.wind_speed_sensor.sensor.when_pressed = self.wind_speed_sensor.press

        if config.SENSORS["rain"]["working"]:
            self.rain_sensor.sensor.when_pressed = self.rain_sensor.press

    def __get_data(self, start_time: float) -> dict:
        """
        Private method to collect data from sensors and calculate wind direction and speed.

        Parameters:
            start_time (float): Time at the start of data collection.

        Returns:
            dict: Dictionary containing data from various sensors.
        """
        data = {}

        if config.SENSORS["wind_direction"]["working"] and self.wind_speed_sensor.get_data() != 0:
            data["direction"] = self.wind_direction_sensor.read_data()
        else:
            data["direction"] = None
            time.sleep(self.wind_direction_sensor.wind_interval)

        if config.SENSORS["wind_speed"]["working"]:
            data["speed"] = self.wind_speed_sensor.read_data(time.time() - start_time)
        else:
            data["speed"] = None

        for sensor in self.sensors:
            res = sensor.read_data()
            data.update(res)

        return data

    def collect_data(self) -> dict:
        """
        Public method to collect data from sensors including wind direction and speed.

        Returns:
            dict: Dictionary containing data from various sensors.
        """
        try:
            self.wind_speed_sensor.clear_data()
            self.rain_sensor.clear_data()

            logging.info(f"{'+' * 15} Starting data collection.")
            start_time = time.time()

            time.sleep(config.MEASURING_TIME - config.MAX_READING_TIME - self.wind_direction_sensor.wind_interval)
            collected_data = self.__get_data(start_time)

            remaining_time = config.MEASURING_TIME - (time.time() - start_time) - 0.04
            if remaining_time < 0:
                logging.error(f"Error occurred during sleep: ValueError: sleep length must be non-negative")
            else:
                time.sleep(remaining_time)

            collected_data["rain"] = self.rain_sensor.read_data() if config.SENSORS["rain"]["working"] else None

            return collected_data

        except Exception as e:
            logging.error(f"Error occurred during reading data from sensors: {str(e)}", exc_info=True)
