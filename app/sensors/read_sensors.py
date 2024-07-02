import time
from datetime import datetime, timedelta

import config
from logger_config import logging

from .other_sensors.TPH_sensor_BME280 import TPHSensor
from .other_sensors.air_quality_sensor_PMS5003 import AirQualitySensor
from .other_sensors.light_sensor_LTR390 import LightSensor
from .weather_meter_sensors.rain_sensor import Rain
from .weather_meter_sensors.wind_direction_sensor import WindDirection
from .weather_meter_sensors.wind_speed_sensor import WindSpeed


class ReadSensors:
    def __init__(self) -> None:
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
        data = {}

        for sensor in self.sensors:
            res = sensor.read_data()
            data.update(res)

        return data

    def next_quarter_hour(self):
        now = datetime.now()
        minutes = now.minute
        minutes_to_next = (15 - minutes % 15) % 15
        if minutes_to_next == 0:
            minutes_to_next = 15
        next_time = now + timedelta(minutes=minutes_to_next)
        next_time = next_time.replace(second=0, microsecond=0)
        return next_time

    def collect_data(self) -> dict:
        try:
            self.wind_speed_sensor.clear_data()
            self.rain_sensor.clear_data()
            collection_start_time = time.time()
            logging.info(f"{'+' * 15} Starting data collection.")

            next_transmission_time = self.next_quarter_hour()
            time_until_transmission = (next_transmission_time - datetime.now()).total_seconds()
            if time_until_transmission < (config.MAX_READING_TIME + 10):
                next_transmission_time += timedelta(minutes=15)
                time_until_transmission = (next_transmission_time - datetime.now()).total_seconds()

            time.sleep(time_until_transmission - config.MAX_READING_TIME)

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

            for _ in range(15):
                current_sensor_readings = self.__get_data()

                for sensor_type in result.keys():
                    sensor_value = current_sensor_readings.get(sensor_type, None)
                    if sensor_value is not None:
                        result[sensor_type].append(sensor_value)
                time.sleep(12)

            self.sensors[2].stop()

            for data_type, measurements in result.items():
                if not measurements:
                    result[data_type] = None
                elif data_type == 'lux':
                    result[data_type] = round(sum(measurements) / len(measurements))
                else:
                    result[data_type] = round(sum(measurements) / len(measurements), 2)

            result["direction"] = self.wind_direction_sensor.read_data()

            time_left_until_transmission = (next_transmission_time - datetime.now()).total_seconds()

            if time_left_until_transmission < 0:
                logging.error("Error occurred during sleep: ValueError: sleep length must be non-negative")
            else:
                time.sleep(time_left_until_transmission)

            collection_duration = time.time() - collection_start_time
            result["speed"] = self.wind_speed_sensor.read_data(collection_duration)
            result["rain"] = self.rain_sensor.read_data()

            if not result["speed"]:
                result["direction"] = None

            return result

        except Exception as e:
            logging.error(f"Error occurred during reading data from sensors: {str(e)}", exc_info=True)
