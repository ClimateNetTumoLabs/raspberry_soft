import bme280
from smbus2 import SMBus
from config import SENSORS
from logger_config import logging

class BME280Sensor:
    def __init__(self):
        conf = SENSORS["bme280"]
        self.working = conf["working"]
        self.bus = conf["port"]
        self.address = conf["address"]
        self.calibration = None
        self.sensor = None

        if self.working:
            self.setup_sensor()
        else:
            logging.info("[BME280] Disabled in config")

    def setup_sensor(self):
        try:
            self.bus = SMBus(self.bus)
            self.calibration = bme280.load_calibration_params(self.bus, self.address)
            self.sensor = True
            logging.info("[BME280] Initialized")
        except Exception as e:
            logging.error(f"[BME280] Init failed: {e}")

    def read_data(self):
        data = {"temperature": None, "pressure": None, "humidity": None}

        if self.working and self.sensor:
            try:
                result = bme280.sample(bus=self.bus, compensation_params=self.calibration)
            except AttributeError as e:
                logging.error(f"Attribute error while reading BME280: {e}")
            except OSError as e:
                logging.error(f"OS error while reading BME280: {e}")
            except Exception as e:
                logging.error(f"Unhandled exception while reading BME280: {e}", exc_info=True)
            else:
                data["temperature"] = round(result.temperature, 2)
                data["pressure"] = round(result.pressure, 2)
                data["humidity"] = round(result.humidity, 2)

        return data

if __name__=="__main__":
    tph = BME280Sensor()
    print(tph.read_data())
