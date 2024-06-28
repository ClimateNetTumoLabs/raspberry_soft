import time

from config import SENSORS
from logger_config import logging
from scripts.kalman_data_collector import KalmanDataCollector
from serial.serialutil import SerialException

from .PMS5003_lib import PMS5003, SerialTimeoutError, ReadTimeoutError, ChecksumMismatchError


class AirQualitySensor:
    def __init__(self) -> None:
        self.sensor = None
        self.sensor_info = SENSORS["air_quality_sensor"]
        self.working = self.sensor_info["working"]

        if self.working:
            self.setup_sensor()

    def setup_sensor(self):
        for i in range(3):
            try:
                self.sensor = PMS5003(
                    device=self.sensor_info["address"],
                    baudrate=self.sensor_info["baudrate"],
                    pin_enable=self.sensor_info["pin_enable"],
                    pin_reset=self.sensor_info["pin_reset"]
                )
                self.stop()
                break
            except Exception as e:
                logging.error(f"Error occurred during creating object for PMS5003 sensor: {e}")

        return self.sensor is not None

    def stop(self):
        self.sensor.stop()

    def read_data(self) -> dict:
        data = {"pm1": None, "pm2_5": None, "pm10": None}

        if self.working:
            if self.sensor is None:
                if not self.setup_sensor():
                    return data

            try:
                all_data = self.sensor.read()
            except SerialTimeoutError as e:
                logging.error(f"SerialTimeout error while reading PMS5003: {e}")
            except ReadTimeoutError as e:
                logging.error(f"ReadTimeout error while reading PMS5003: {e}")
            except SerialException as e:
                logging.error(f"SerialException error while reading PMS5003: {e}")
            except ChecksumMismatchError as e:
                logging.error(f"ChecksumMismatch error while reading PMS5003: {e}")
            except Exception as e:
                logging.error(f"Unhandled exception while reading PMS5003: {e}", exc_info=True)
            else:
                data["pm1"] = all_data.pm_ug_per_m3(size=1.0)
                data["pm2_5"] = all_data.pm_ug_per_m3(size=2.5)
                data["pm10"] = all_data.pm_ug_per_m3(size=10)

        return data

