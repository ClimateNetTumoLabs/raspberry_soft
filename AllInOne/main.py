import time
import logging
from db import Database
from Sensors import AirQualitySensor, CO2Sensor, LightSensor, TPHSensor
from WeatherMeterSensors import WeatherSensors
from datetime import datetime


logging.basicConfig(filename='parsing.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def read_sensor_data(sensors):
    data = {}

    for sensor, name in sensors.items():
        res = sensor.read_data()
        if type(res) == dict:
            data.update(res)
        elif type(res) == int:
            data[name] = res
    
    return data


def add_data(data_all, data):
    for key, value in data.items():
        if key == "direction" and value is None:
            continue
        if key not in data_all:
            data_all[key] = [value]
        else:
            data_all[key].append(value)
    return data_all


def get_averages(data, weather):
    result_data = {}
    for key, values in data.items():
        if key == "direction":
            result_data[key] = weather.get_direction_label(values)
        else:
            result_data[key] = round(sum(values) / len(values), 2)
    
    return result_data


def main(measuring_time, light_obj, tph_obj, air_quality_obj, co2_obj, weather):

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
            data = read_sensor_data(sensors)
            data_all = add_data(data_all, data)
            
            remaining_time = measuring_time - (time.time() - start_time)
            if remaining_time <= 30:
                time.sleep(remaining_time)

        data_all["direction"] = data_all.get("direction")

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
            data = main(900, light_obj, tph_obj, air_quality_obj, co2_obj, weather)

            data_avg = get_averages(data, weather)

            insert_data = list(data_avg.values())
            insert_data.insert(0, datetime.now())

            db.insert_data(insert_data)

            logging.info("Data successfully inserted into the database.")
        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)
