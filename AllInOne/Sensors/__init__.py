import time
from .WeatherMeterSensors import *
from .OtherSensors import *
from logger_config import *
from config import *


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

    def __init__(self):
        self.__create_sensor_objects()

        self.wind_direction_sensor = WindDirection()
        self.wind_speed_sensor = WindSpeed()
        self.rain_sensor = Rain()

        self.MEASURING_TIME = MEASURING_TIME
        self.MAX_READING_TIME = MAX_READING_TIME

        if SENSORS["wind_speed"]:
            self.wind_speed_sensor.sensor.when_pressed = self.wind_speed_sensor.press
        
        if SENSORS["rain"]:
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

        for sensor in sensor_name_mapping:
            sensor_name_mapping[sensor]['read'] = SENSORS[sensor_name_mapping[sensor]['variable_name']]

        self.sensors = []

        for sensor, params in sensor_name_mapping.items():
            setattr(self, params["variable_name"], sensor(read=params["read"]))
            self.sensors.append(self.__dict__[params["variable_name"]])

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
        data = {}

        
        if self.wind_speed_sensor.get_data() != 0 and SENSORS["wind_direction"]:
            data["direction"] = self.wind_direction_sensor.read_data()
        else:
            data["direction"] = None
            time.sleep(self.wind_direction_sensor.wind_interval)
        
        data["speed"] = self.wind_speed_sensor.read_data(time.time() - start_time) if SENSORS["wind_speed"] else None
        
        for sensor in self.sensors:
            res = sensor.read_data()
            data.update(res)

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

            time.sleep(self.MEASURING_TIME - self.MAX_READING_TIME - self.wind_direction_sensor.wind_interval)
            collected_data = self.__get_data(start_time)

            remaining_time = self.MEASURING_TIME - (time.time() - start_time) - 0.04
            if remaining_time < 0:
                logging.error(f"Error occurred during sleep: ValueError: sleep length must be non-negative")
            else:
                time.sleep(remaining_time)
            
            collected_data["rain"] = self.rain_sensor.read_data() if SENSORS["rain"] else None
            return collected_data

        except Exception as e:
            logging.error(f"Error occurred during reading data from sensors: {str(e)}", exc_info=True)
