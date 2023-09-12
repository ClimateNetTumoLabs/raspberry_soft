import time
import logging
from datetime import datetime
from WeatherMeterSensors import Rain, WindDirection, WindSpeed
from Sensors import AirQualitySensor, CO2Sensor, LightSensor, TPHSensor


logging.basicConfig(filename='parsing.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ReadSensor:
    def __init__(self, measuring_time=300, max_reading_time=30):
        self.air_quality_sensor = AirQualitySensor()
        self.co2_sensor = CO2Sensor()
        self.light_sensor = LightSensor()
        self.tph_sensor = TPHSensor()
        self.wind_direction_sensor = WindDirection()
        self.wind_speed_sensor = WindSpeed()
        self.rain_sensor = Rain()

        self.sensor_name_mapping = {
            self.light_sensor: "Light",
            self.tph_sensor: "TPH",
            self.air_quality_sensor: "AirQuality",
            self.co2_sensor: "CO2"
        }

        self.MEASURING_TIME = measuring_time
        self.MAX_READING_TIME = max_reading_time

        self.wind_speed_sensor.sensor.when_pressed = self.wind_speed_sensor.press
        self.rain_sensor.sensor.when_pressed = self.rain_sensor.press

        self.old_speed_count = self.rain_sensor.count

    def __add_data(self, data):
        time.sleep(20)

        if self.old_speed_count != self.rain_sensor.count:
            self.old_speed_count = self.rain_sensor.count
            direction = self.wind_direction_sensor.read_data()
        else:
            direction = None

        for sensor, name in self.sensor_name_mapping.items():
            res = sensor.read_data()

            if isinstance(res, dict):
                for key, value in res.items():
                    data.setdefault(key, []).append(value)
            else:
                data.setdefault(name, []).append(res)

        data.setdefault("speed", [])
        data.setdefault("rain", [])
        data.setdefault("direction", []).append(direction)

        return data

    def __calculate_averages(self, data):
        result_data = {}

        for key, values in data.items():
            values = [value for value in values if value is not None]

            if not values:
                result_data[key] = None
                continue

            if key == "direction":
                result_data[key] = self.wind_direction_sensor.get_direction_label(sum(values) / len(values))
            else:
                result_data[key] = round(sum(values) / len(values), 2)

        return result_data

    def collect_data(self):
        try:
            logging.info("Starting data collection.")

            collected_data = {}

            start_time = time.time()
            while time.time() - start_time < self.MEASURING_TIME:
                collected_data = self.__add_data(collected_data)

                remaining_time = self.MEASURING_TIME - (time.time() - start_time)
                if remaining_time <= self.MAX_READING_TIME:
                    time.sleep(remaining_time)

            collected_data["speed"].append(self.wind_speed_sensor.read_data(time.time() - start_time))
            collected_data["rain"].append(self.rain_sensor.read_data())

            logging.info("Data collection completed.")

            return collected_data

        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)

    def get_averages_list(self, data):
        averages_data = self.__calculate_averages(data)

        result_lst = [datetime.now()] + list(averages_data.values())

        return result_lst
