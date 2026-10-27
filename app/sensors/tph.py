from .bme280 import BME280Sensor
from .sht45 import SHT45Sensor

class TPHSensor:
    """
    Temperature and humidity from the SHT45 when it is on in config, pressure
    always from the BME280. With the SHT45 off, all three come from the BME280.
    """
    def __init__(self):
        self.bme280 = BME280Sensor()
        self.sht45 = SHT45Sensor()

    def read_data(self):
        data = self.bme280.read_data()

        # No fallback to the BME280: a failed SHT45 reading is sent as null.
        if self.sht45.working:
            sht = self.sht45.read_data()
            data["temperature"] = sht["temperature"]
            data["humidity"] = sht["humidity"]

        return data
