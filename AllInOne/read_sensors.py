import time
from WeatherMeterSensors import *
from Sensors import *
from logger_config import *


class ReadSensor:
    """
    ReadSensor class is responsible for collecting data from various sensors used in the ClimateNet project, including LightSensor
    (BH1750), TPHSensor (BME280), AirQualitySensor (PMS5003), WindDirection (SEN15901), WindSpeed (SEN15901), and Rain (SEN15901)
    sensors. The collected data represents environmental information such as light levels, temperature, pressure, humidity, air quality,
    wind direction, wind speed, and rain data.

    Parameters:
    measuring_time (int): The total time in seconds to collect data from all sensors.
    max_reading_time (int): The maximum time in seconds allowed for individual sensor readings.

    Attributes:
    MEASURING_TIME (int): The total measuring time in seconds.
    MAX_READING_TIME (int): The maximum time allowed for individual sensor readings.
    """

    def __init__(self, measuring_time=900, max_reading_time=340):
        self.__create_sensor_objects()

        self.wind_direction_sensor = WindDirection()
        self.wind_speed_sensor = WindSpeed()
        self.rain_sensor = Rain()

        self.MEASURING_TIME = measuring_time
        self.MAX_READING_TIME = max_reading_time

        self.wind_speed_sensor.sensor.when_pressed = self.wind_speed_sensor.press
        self.rain_sensor.sensor.when_pressed = self.rain_sensor.press

    def __create_sensor_objects(self):
        """
        Initialize sensor objects for LightSensor (BH1750), TPHSensor (BME280), and AirQualitySensor (PMS5003).

        This method creates instances of LightSensor, TPHSensor, and AirQualitySensor and associates them with class attributes
        for easy access.

        Attributes:
        light_sensor (LightSensor): An instance of the LightSensor (BH1750).
        tph_sensor (TPHSensor): An instance of the TPHSensor (BME280).
        air_quality_sensor (AirQualitySensor): An instance of the AirQualitySensor (PMS5003).
        sensor_name_mapping (dict): A dictionary mapping sensor instances to their respective names.
        """

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
        """
        Retrieve data from all sensors and return it as a dictionary.

        This method collects data from all registered sensors and combines them into a dictionary.

        Parameters:
        start_time (float): The time at which data collection started.

        Returns:
        dict: A dictionary containing sensor data, including light (BH1750), temperature, pressure, humidity (BME280),
        air quality (PMS5003), wind speed, and wind direction (SEN15901), as well as rain data (SEN15901).

        The dictionary may have the following keys:
        - "Light": LightSensor (BH1750) reading (float).
        - "temperature": TPHSensor (BME280) temperature reading (float).
        - "pressure": TPHSensor (BME280) pressure reading (float).
        - "humidity": TPHSensor (BME280) humidity reading (float).
        - "Air_PM1": AirQualitySensor (PMS5003) reading for PM1 (int).
        - "Air_PM2_5": AirQualitySensor (PMS5003) reading for PM2.5 (int).
        - "Air_PM10": AirQualitySensor (PMS5003) reading for PM10 (int).
        - "speed": Wind speed reading (float).
        - "rain": Rainfall amount in millimeters (float).
        - "direction": Wind direction reading (str) if wind speed is not zero; otherwise, None.

        """
        if self.wind_speed_sensor.get_data() != 0:
            direction = self.wind_direction_sensor.read_data()
        else:
            direction = None
            time.sleep(300)
            
        direction = self.wind_direction_sensor.read_data() if self.wind_speed_sensor.get_data() != 0 else None
        data = {}

        for sensor, name in self.sensor_name_mapping.items():
            res = sensor.read_data()
            if isinstance(res, dict):
                data.update(res)
            else:
                data[name] = res

        data["speed"] = self.wind_speed_sensor.read_data(time.time() - start_time)
        data["rain"] = 0.0
        data["direction"] = direction
        return data

    def collect_data(self):
        """
        Collect data from sensors and return it as a dictionary.

        This method initiates the data collection process, including sensor readings from all sensors. It also handles
        timing constraints for data collection and includes rain data (SEN15901).

        Returns:
        dict: A dictionary containing sensor data collected during the measuring time.

        The dictionary may have the following keys:
        - "Light": LightSensor (BH1750) reading (float).
        - "temperature": TPHSensor (BME280) temperature reading (float).
        - "pressure": TPHSensor (BME280) pressure reading (float).
        - "humidity": TPHSensor (BME280) humidity reading (float).
        - "Air_PM1": AirQualitySensor (PMS5003) reading for PM1 (int).
        - "Air_PM2_5": AirQualitySensor (PMS5003) reading for PM2.5 (int).
        - "Air_PM10": AirQualitySensor (PMS5003) reading for PM10 (int).
        - "speed": Wind speed reading (float).
        - "rain": Rainfall amount in millimeters (float).

        """
        try:
            self.wind_speed_sensor.clear_data()
            self.rain_sensor.clear_data()
            logging.info(f"{'+' * 15} Starting data collection.")
            start_time = time.time()

            time.sleep(self.MEASURING_TIME - self.MAX_READING_TIME)
            collected_data = self.__get_data(start_time)

            remaining_time = self.MEASURING_TIME - (time.time() - start_time) - 0.04
            
            if remaining_time < 0:
                logging.error(f"Error occurred during sleep: ValueError: sleep length must be non-negative")
            else:
                time.sleep(remaining_time)

            collected_data["rain"] = self.rain_sensor.read_data()
            return collected_data

        except Exception as e:
            logging.error(f"Error occurred during reading data from sensors: {str(e)}", exc_info=True)
