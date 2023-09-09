import time
import logging
from db import Database
from Sensors import AirQualitySensor, CO2Sensor, LightSensor, TPHSensor
from WeatherMeterSensors import WeatherSensors
from datetime import datetime
from network_check import check_network


logging.basicConfig(filename='parsing.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

MEASURING_TIME = 900
MAX_SENSORS_READING_TIME = 30


def calculate_averages(data, weather):
    result_data = {}

    for key, values in data.items():
        values = list(filter(None, values))

        if not values:
            result_data[key] = None
            continue

        if key == "direction":
            result_data[key] = weather.get_direction_label(values)
        else:
            result_data[key] = round(sum(values) / len(values), 2)

    
    return result_data


def get_averages_list(data, weather):
    averages_data = calculate_averages(data, weather)

    result_lst = [datetime.now()] + list(averages_data.values())

    return result_lst


def add_data(data, sensor_name_mapping):
    for sensor, name in sensor_name_mapping.items():
        res = sensor.read_data()

        if isinstance(res, dict):
            for key, value in res.items():
                data.setdefault(key, []).append(value)
        else:
            data.setdefault(name, []).append(res)
    
    return data


def collect_data(sensor_name_mapping, measuring_time, max_reading_time):
    try:
        logging.info("Starting data collection.")
        
        collected_data = {}

        start_time = time.time()

        while time.time() - start_time < measuring_time:
            collected_data = add_data(collected_data, sensor_name_mapping)
            
            remaining_time = measuring_time - (time.time() - start_time)
            if remaining_time <= max_reading_time:
                time.sleep(remaining_time)

        logging.info("Data collection completed.")

        return collected_data
        
    except Exception as e:
        logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)


if __name__ == "__main__":
    check_network()
    
    weather = WeatherSensors()
    sensor_name_mapping = {
        LightSensor(): "Light",
        TPHSensor(): "TPH",
        AirQualitySensor(): "AirQuality",
        CO2Sensor(): "CO2",
        weather: "Weather"
    }

    db = Database()

    while True:
        try:
            collected_data = collect_data(sensor_name_mapping, MEASURING_TIME, 
                                          MAX_SENSORS_READING_TIME)
            average_data_lst = get_averages_list(collected_data, weather)
            db.insert_data(average_data_lst)
        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)
