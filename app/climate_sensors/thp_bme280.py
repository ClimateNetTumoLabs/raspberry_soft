from base_sensor import BaseSensor
from smbus2 import SMBus
import bme280

class BME280Sensor(BaseSensor):
    def __init__(self, config_manager):
        super().__init__(config_manager, "thp_bme280")
        self.bus, self.address, self.calibration = self._init_sensor()

    def _init_sensor(self):
        port = 1
        address = 0x76
        bus = SMBus(port)
        calibration = bme280.load_calibration_params(bus, address)
        return bus, address, calibration

    def _read_sensor(self):
        data = bme280.sample(self.bus, self.address, self.calibration)
        return {
            "temperature": data.temperature,
            "humidity": data.humidity,
            "pressure": data.pressure,
        }
