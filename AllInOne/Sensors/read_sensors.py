import time
from .WeatherMeterSensors import *
from .OtherSensors import *
from logger_config import *
import config


class ReadSensors:
    def __init__(self):
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

    def __get_data(self, start_time):
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

    def collect_data(self):
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
