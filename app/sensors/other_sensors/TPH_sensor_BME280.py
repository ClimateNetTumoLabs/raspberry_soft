import time

import bme280
import smbus2
from config import SENSORS
from logger_config import logging
from scripts.kalman_data_collector import KalmanDataCollector


class TPHSensor:
    def __init__(self):
        self.calibration_params = None
        self.sensor_info = SENSORS["tph_sensor"]
        self.working = self.sensor_info["working"]
        self.port = self.sensor_info["port"]
        self.bus = smbus2.SMBus(self.port)
        self.sensor = None

        if self.working:
            self.setup_sensor()

    def setup_sensor(self):
        for i in range(3):
            try:
                self.calibration_params = bme280.load_calibration_params(self.bus)
                self.sensor = True
                break
            except Exception as e:
                logging.error(f"Error occurred during creating object for BME280 sensor: {e}")

        return self.sensor is not None

    def read_data(self) -> dict:
        data = {"temperature": None, "pressure": None, "humidity": None}

        if self.working:
            if not self.sensor:
                if not self.setup_sensor():
                    return data
            try:
                result = bme280.sample(bus=self.bus, compensation_params=self.calibration_params)
            except AttributeError as e:
                logging.error(f"Attribute error while reading BME280: {e}")
            except Exception as e:
                logging.error(f"Unhandled exception while reading BME280: {e}", exc_info=True)
            else:
                data["temperature"] = round(result.temperature, 2)
                data["pressure"] = round(result.pressure * 0.750061, 2)
                data["humidity"] = round(result.humidity, 2)

        return data
