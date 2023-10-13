import time
from WeatherMeterSensors import *
from Sensors import *
from logger_config import *


class ReadSensor:
    def __init__(self, measuring_time=900, max_reading_time=15):
        self.__create_sensor_objects()

        self.wind_direction_sensor = WindDirection()
        self.wind_speed_sensor = WindSpeed()
        self.rain_sensor = Rain()

        self.MEASURING_TIME = measuring_time
        self.MAX_READING_TIME = max_reading_time

        self.wind_speed_sensor.sensor.when_pressed = self.wind_speed_sensor.press
        self.rain_sensor.sensor.when_pressed = self.rain_sensor.press

    def __create_sensor_objects(self):
        sensors = {
            LightSensor: {
                "variable_name": "light_sensor",
                "name": "Light"
            },
            TPHSensor: {
                "variable_name": "tph_sensor",
                "name": "TPH"
            },
            AirQualitySensor: {
                "variable_name": "air_quality_sensor",
                "name": "AirQuality"
            }
        }
        
        self.sensor_name_mapping = {}

        for sensor, names in sensors.items():
            setattr(self, names["variable_name"], sensor())
            self.sensor_name_mapping[self.__dict__[names["variable_name"]]] = names["name"]

    def __get_data(self, start_time):
        data = {}

        for sensor, name in self.sensor_name_mapping.items():
            res = sensor.read_data()
            if isinstance(res, dict):
                 data.update(res)
            else:
                data[name] = res

        data["speed"] = self.wind_speed_sensor.read_data(time.time() - start_time)
        data["rain"] = 0.0
        data["direction"] = self.wind_direction_sensor.read_data() if data["speed"] != 0 else None
        return data

    def get_data(self):
        try:
            self.wind_speed_sensor.clear_data()
            self.rain_sensor.clear_data()
            logging.info(f"{'+' * 15} Starting data collection.")
            start_time = time.time()

            time.sleep(self.MEASURING_TIME - self.MAX_READING_TIME)
            collected_data = self.__get_data(start_time)

            remaining_time = self.MEASURING_TIME - (time.time() - start_time)
            time.sleep(remaining_time)

            collected_data["rain"] = self.rain_sensor.read_data()
            return collected_data

        except Exception as e:
            logging.error(f"Error occurred during reading data from sensors: {str(e)}", exc_info=True)

