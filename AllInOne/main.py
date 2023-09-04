import time
import logging
from db import Database
from Sensors import AirQualitySensor, CO2Sensor, LightSensor, TPHSensor
from WeatherMeterSensors import WeatherSensors
from datetime import datetime


logging.basicConfig(filename='parsing.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def add_data(data, sensors):
    try:
        for sensor, name in sensors.items():
            res = sensor.read_data()

            if type(res) == dict:
                for key, value in res:
                    if key in data:
                        data[key].append(value)
                    else:
                        data[key] = [value]
            elif type(res) == int:
                if name in data:
                    data[name].append(res)
                else:
                    data[name] = [res]
        
        return data
    except Exception as e:
            logging.error(f"Error occurred during reading data: {str(e)}", exc_info=True)


def remove_none(lst):
    new_lst = [elem for elem in lst if elem is not None]
    return new_lst


def get_averages_list(data, weather):
    result_data = {}

    for key, values in data.items():
        values = remove_none(values)
        if values:
            if key == "direction":
                result_data[key] = weather.get_direction_label(values)
            else:
                result_data[key] = round(sum(values) / len(values), 2)
        else:
            result_data[key] = None

    result_lst = list(result_data.items())
    result_lst.insert(0, datetime.now())

    return result_lst


def read_data(measuring_time, light_obj, tph_obj, air_quality_obj, co2_obj, weather):

    try:
        logging.info("Starting data collection.")
        
        sensors = {
            light_obj: "Light",
            tph_obj: "",
            air_quality_obj: "",
            co2_obj: "CO2",
            weather: ""
        }

        data_all = {}

        start_time = time.time()

        while time.time() - start_time < measuring_time:
            data_all = add_data(data_all, sensors)
            
            remaining_time = measuring_time - (time.time() - start_time)
            if remaining_time <= 30:
                time.sleep(remaining_time)

        logging.info("Data collection completed.")

        return data_all
        
    except Exception as e:
        logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)


if __name__ == "__main__":
    
    light_obj = LightSensor() 
    tph_obj = TPHSensor()
    air_quality_obj = AirQualitySensor()
    co2_obj = CO2Sensor()
    weather = WeatherSensors()
    db = Database()

    while True:
        try:
            data = read_data(900, light_obj, tph_obj, air_quality_obj, co2_obj, weather)
            data_lst = get_averages_list(data, weather)
            db.insert_data(data_lst)

        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)
