import time

import config

from .weather_meter_sensors.rain_sensor import Rain
from .weather_meter_sensors.wind_direction_sensor import WindDirection
from .weather_meter_sensors.wind_speed_sensor import WindSpeed

from .other_sensors.air_quality_sensor_PMS5003 import AirQualitySensor
from .other_sensors.light_sensor_LTR390 import LightSensor
from .other_sensors.TPH_sensor_BME280 import TPHSensor

from logger_config import logging


class ReadSensors:
    """
    Represents a data collector for various environmental sensors.

    This class collects data from a variety of sensors, including light sensors, temperature, pressure, and humidity
    sensors, air quality sensors, wind direction sensors, wind speed sensors, and rain sensors. It compiles
    the collected data into a dictionary for further processing or logging.

    Attributes:
        sensors (list): A list of sensor objects for light, temperature, pressure, humidity, and air quality
        measurements.
        wind_direction_sensor (WindDirection): An instance of the WindDirection class for measuring wind direction.
        wind_speed_sensor (WindSpeed): An instance of the WindSpeed class for measuring wind speed.
        rain_sensor (Rain): An instance of the Rain class for measuring rainfall.

    Methods:
        collect_data() -> dict: Collects data from all sensors and returns a dictionary containing the collected data.

    """

    def __init__(self) -> None:
        """
        Initializes the ReadSensors object.

        Creates instances of various sensor classes for collecting environmental data, including light, temperature,
        pressure, humidity, air quality, wind direction, wind speed, and rain sensors.
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
        Retrieves data from all sensors.

        Args:
            start_time (float): The start time of the data collection process.

        Returns:
            dict: A dictionary containing the collected sensor data.
        """
        data = {"speed": None, "direction": None}

        if config.SENSORS["wind_speed"]["working"]:
            data["speed"] = self.wind_speed_sensor.read_data(time.time() - start_time)

        if config.SENSORS["wind_direction"]["working"] and data["speed"]:
            data["direction"] = self.wind_direction_sensor.read_data()
        else:
            time.sleep(self.wind_direction_sensor.wind_interval)

        for sensor in self.sensors:
            res = sensor.read_data()
            data.update(res)

        return data

    def collect_data(self) -> dict:
        """
        Collects data from all sensors and returns a dictionary containing the collected data.

        Returns:
            dict: A dictionary containing the collected sensor data.
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
                logging.error("Error occurred during sleep: ValueError: sleep length must be non-negative")
            else:
                time.sleep(remaining_time)

            collected_data["rain"] = self.rain_sensor.read_data() if config.SENSORS["rain"]["working"] else None

            return collected_data

        except Exception as e:
            logging.error(f"Error occurred during reading data from sensors: {str(e)}", exc_info=True)
