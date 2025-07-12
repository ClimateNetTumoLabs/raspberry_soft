import time
from datetime import datetime, timedelta

import config
from logger_config import logging

from .other_sensors.TPH_sensor_BME280 import TPHSensor
from .other_sensors.air_quality_sensor_SPS30 import AirQualitySensor
from .other_sensors.light_sensor_LTR390 import LightSensor
from .weather_meter_sensors.rain_sensor import Rain
from .weather_meter_sensors.wind_direction_sensor import WindDirection
from .weather_meter_sensors.wind_speed_sensor import WindSpeed


class ReadSensors:
    """
    Class to read data from various sensors and collect it periodically.

    Attributes:
        sensors (list): List of sensor objects.
        wind_direction_sensor (WindDirection): Instance of WindDirection sensor.
        wind_speed_sensor (WindSpeed): Instance of WindSpeed sensor.
        rain_sensor (Rain): Instance of Rain sensor.
    """

    def __init__(self) -> None:
        """
        Initializes sensor instances and sets up event handlers for wind and rain sensors.
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

    def __get_data(self) -> dict:
        """
        Reads data from all sensors and returns a dictionary of sensor readings.

        Returns:
            dict: Dictionary containing sensor readings.
        """
        data = {}

        for sensor in self.sensors:
            res = sensor.read_data()
            data.update(res)

        return data

    def next_quarter_hour(self) -> datetime:
        """
        Calculates the next quarter-hour timestamp from the current time.

        Returns:
            datetime: Next quarter-hour timestamp.
        """
        now = datetime.now()
        minutes = now.minute
        minutes_to_next = (15 - minutes % 15) % 15
        if minutes_to_next == 0:
            minutes_to_next = 15
        next_time = now + timedelta(minutes=minutes_to_next)
        next_time = next_time.replace(second=0, microsecond=0)
        return next_time

    def next_send_time(self) -> datetime:
        """
        Calculates the next send time based on configured interval.
        """
        now = datetime.now()
        interval = config.DATA_SEND_INTERVAL_MINUTES
        minutes = now.minute
        minutes_to_next = (interval - minutes % interval) % interval
        if minutes_to_next == 0:
            minutes_to_next = interval
        next_time = now + timedelta(minutes=minutes_to_next)
        return next_time.replace(second=0, microsecond=0)

    def collect_data(self) -> dict:
        """
        Collects sensor data over a period and returns aggregated results.

        Returns:
            dict: Dictionary containing aggregated sensor data.
        """
        try:
            self.wind_speed_sensor.clear_data()
            self.rain_sensor.clear_data()
            collection_start_time = time.time()
            logging.info(f"{'+' * 15} Starting data collection.")

            # Calculate next transmission time
            next_transmission_time = self.next_send_time()
            time_until_transmission = (next_transmission_time - datetime.now()).total_seconds()

            # Adjust next transmission time if it's too close
            if time_until_transmission < (config.MAX_READING_TIME + 10):
                next_transmission_time += timedelta(minutes=15)
                time_until_transmission = (next_transmission_time - datetime.now()).total_seconds()

            # Wait until it's time to collect data
            time.sleep(time_until_transmission - config.MAX_READING_TIME)

            # Initialize result data structure
            result = {
                "uv": [],
                "lux": [],
                "temperature": [],
                "humidity": [],
                "pressure": [],
                "pm1": [],
                "pm2_5": [],
                "pm10": []
            }
            self.sensors[2].start()
            # Collect sensor data over 15 iterations
            self.sensors[2].start()
            for _ in range(15):
                current_sensor_readings = self.__get_data()

                # Aggregate data into result structure
                for sensor_type in result.keys():
                    sensor_value = current_sensor_readings.get(sensor_type, None)
                    if sensor_value is not None:
                        result[sensor_type].append(sensor_value)
                time.sleep(12)

            # Stop air quality sensor after readings
            self.sensors[2].stop()

            # Calculate averages for sensor data
            for data_type, measurements in result.items():
                if not measurements:
                    result[data_type] = None
                elif data_type == 'lux' or data_type == 'uv':
                    result[data_type] = round(sum(measurements) / len(measurements))
                else:
                    result[data_type] = round(sum(measurements) / len(measurements), 2)

            # Read wind direction and speed, as well as rain data
            result["direction"] = self.wind_direction_sensor.read_data()

            # Sleep until next transmission time
            time_left_until_transmission = (next_transmission_time - datetime.now()).total_seconds()
            if time_left_until_transmission < 0:
                logging.error("Error occurred during sleep: ValueError: sleep length must be non-negative")
            else:
                time.sleep(time_left_until_transmission)

            # Calculate collection duration and read wind speed and rain data
            collection_duration = time.time() - collection_start_time
            result["speed"] = self.wind_speed_sensor.read_data(collection_duration)
            result["rain"] = self.rain_sensor.read_data()

            # If speed data is None, set direction to None
            if not result["speed"]:
                result["direction"] = None

            return result

        except Exception as e:
            logging.error(f"Error occurred during reading data from sensors: {str(e)}", exc_info=True)
