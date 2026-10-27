from logger_config import logging
from .bme280 import BME280Sensor
from .sht45 import SHT45Sensor

class TPHSensor:
    """
    Temperature and humidity from the SHT45 if it initialized, otherwise from
    the BME280. Pressure always from the BME280.
    """
    def __init__(self):
        self.bme280 = BME280Sensor()
        self.sht45 = SHT45Sensor()
        # Decided once at startup: a disabled or failed SHT45 falls back to the BME280.
        self.use_sht45 = self.sht45.sensor is not None
        logging.info(f"[TPH] Temperature and humidity from {'SHT45' if self.use_sht45 else 'BME280'}")

    def read_data(self):
        data = self.bme280.read_data()

        # No fallback once running: a failed SHT45 reading is sent as null.
        if self.use_sht45:
            sht = self.sht45.read_data()
            data["temperature"] = sht["temperature"]
            data["humidity"] = sht["humidity"]

        return data
