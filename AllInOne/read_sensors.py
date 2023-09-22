import time
import logging
from datetime import datetime
from WeatherMeterSensors import Rain, WindDirection, WindSpeed
from Sensors import AirQualitySensor, CO2Sensor, LightSensor, TPHSensor


logging.basicConfig(filename='parsing.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ReadSensor:
    def __init__(self, measuring_time=60, max_reading_time=30):
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
            },
            CO2Sensor: {
                "variable_name": "co2_sensor",
                "name": "CO2"
            }
        }

        self.wind_direction_sensor = WindDirection()
        self.wind_speed_sensor = WindSpeed()
        self.rain_sensor = Rain()

        self.sensor_name_mapping = {}
        for sensor, names in sensors.items():
            setattr(self, names["variable_name"], sensor())
            self.sensor_name_mapping[self.__dict__[names["variable_name"]]] = names["name"]

        self.MEASURING_TIME = measuring_time
        self.MAX_READING_TIME = max_reading_time

        self.wind_speed_sensor.sensor.when_pressed = self.wind_speed_sensor.press
        self.rain_sensor.sensor.when_pressed = self.rain_sensor.press

    def __get_data(self):
        time.sleep(self.MEASURING_TIME - self.MAX_READING_TIME)
        data = {}
        for sensor, name in self.sensor_name_mapping.items():
            res = sensor.read_data()
            if isinstance(res, dict):
                 data.update(res)
            else:
                data[name] = res

        data["speed"] = 0.0
        data["rain"] = 0.0
        data["direction"] = None
        return data

    def collect_data(self):
        try:
            self.wind_speed_sensor.clear_data()
            self.rain_sensor.clear_data()
            logging.info("Starting data collection.")
            start_time = time.time()
            collected_data = self.__get_data()
            
            if self.wind_speed_sensor.count != 0:
                collected_data["direction"] = self.wind_direction_sensor.read_data()

            remaining_time = self.MEASURING_TIME - (time.time() - start_time)
            time.sleep(remaining_time)
            collected_data["speed"] = self.wind_speed_sensor.read_data(time.time() - start_time)
            collected_data["rain"] = self.rain_sensor.read_data()
            logging.info("Data collection completed.")

            for key, value in collected_data.items():
                print(f"{key}  ->  {value}")

            print("\n" + ("#" * 50) + "\n")

            return collected_data

        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)

