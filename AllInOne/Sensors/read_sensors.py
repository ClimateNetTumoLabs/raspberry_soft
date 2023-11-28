import time
from .WeatherMeterSensors import *
from .OtherSensors import *
from logger_config import *
from config import *


class ReadSensors:
    def __init__(self):
        self.__create_sensor_objects()

        self.wind_direction_sensor = WindDirection()
        self.wind_speed_sensor = WindSpeed()
        self.rain_sensor = Rain()

        self.MEASURING_TIME = MEASURING_TIME
        self.MAX_READING_TIME = MAX_READING_TIME

        if SENSORS["wind_speed"]["working"]:
            self.wind_speed_sensor.sensor.when_pressed = self.wind_speed_sensor.press
        
        if SENSORS["rain"]["working"]:
            self.rain_sensor.sensor.when_pressed = self.rain_sensor.press

    def __create_sensor_objects(self):
        sensor_name_mapping = {
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

        self.sensors = []

        for sensor, params in sensor_name_mapping.items():
            setattr(self, params["variable_name"], sensor())
            self.sensors.append(self.__dict__[params["variable_name"]])
    
    def __calculate_altitude(self, pressure, temperature, sea_level_altitude=1013):
        if not SENSORS["altitude"]["working"]:
            return None
        
        return ((sea_level_altitude / pressure) ** (1 / 5.257) - 1) * ((temperature + 273.15) / 0.0065)

    def __get_data(self, start_time):
        data = {}
        
        if self.wind_speed_sensor.get_data() != 0 and SENSORS["wind_direction"]["working"]:
            data["direction"] = self.wind_direction_sensor.read_data()
        else:
            data["direction"] = None
            time.sleep(self.wind_direction_sensor.wind_interval)
        
        data["speed"] = self.wind_speed_sensor.read_data(time.time() - start_time) if SENSORS["wind_speed"]["working"] else None
        
        for sensor in self.sensors:
            res = sensor.read_data()
            data.update(res)
        
        if data["temperature"] and data["pressure"]:
            data['altitude'] = self.__calculate_altitude(pressure=data["pressure"], temperature=data["temperature"])

        return data

    def collect_data(self):
        try:
            self.wind_speed_sensor.clear_data()
            self.rain_sensor.clear_data()
            logging.info(f"{'+' * 15} Starting data collection.")
            start_time = time.time()

            time.sleep(self.MEASURING_TIME - self.MAX_READING_TIME - self.wind_direction_sensor.wind_interval)
            collected_data = self.__get_data(start_time)

            remaining_time = self.MEASURING_TIME - (time.time() - start_time) - 0.04
            if remaining_time < 0:
                logging.error(f"Error occurred during sleep: ValueError: sleep length must be non-negative")
            else:
                time.sleep(remaining_time)
            
            collected_data["rain"] = self.rain_sensor.read_data() if SENSORS["rain"]["working"] else None
            return collected_data

        except Exception as e:
            logging.error(f"Error occurred during reading data from sensors: {str(e)}", exc_info=True)
