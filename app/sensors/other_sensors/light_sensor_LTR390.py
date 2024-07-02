import adafruit_ltr390
import board
import busio
from config import SENSORS
from logger_config import logging


class LightSensor:
    def __init__(self) -> None:
        self.sensor = None
        self.i2c = None
        self.sensor_info = SENSORS["light_sensor"]
        self.working = self.sensor_info["working"]

        if self.working:
            self.setup_sensor()

    def setup_sensor(self):
        for i in range(3):
            try:
                self.i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = adafruit_ltr390.LTR390(self.i2c)
                break
            except Exception as e:
                logging.error(f"Error occurred during creating object for LTR390 sensor: {e}")

        return self.sensor is not None

    def read_data(self) -> dict:
        data = {"uv": None, "lux": None}

        if self.working:
            if self.sensor is None:
                if not self.setup_sensor():
                    return data

            try:
                uvi = self.sensor.uvi
                lux = self.sensor.lux
            except AttributeError as e:
                logging.error(f"Attribute error while reading LTR390: {e}")
            except Exception as e:
                logging.error(f"Unhandled exception while reading LTR390: {e}", exc_info=True)
            else:
                data["uv"] = round(uvi, 2)
                data["lux"] = round(lux)

        return data
