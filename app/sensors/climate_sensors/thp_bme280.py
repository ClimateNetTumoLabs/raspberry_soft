from ..base_sensor import BaseSensor
from smbus2 import SMBus
import bme280

class BME280Sensor(BaseSensor):
    def __init__(self, config_manager):
        super().__init__(config_manager, "thp_bme280")
        if not self.enabled:
            return

        self.bus, self.address, self.calibration = self._init_sensor()

    def _init_sensor(self):
        cfg = self.config.get_sensor_config(self.name)
        port = cfg.get("port", 1)
        address = cfg.get("address", 0x76)

        bus = SMBus(port)
        calibration = bme280.load_calibration_params(bus, address)
        return bus, address, calibration

    def _read_sensor(self):
        if not self.enabled:
            return None

        data = bme280.sample(self.bus, self.address, self.calibration)
        return {
            "temperature": data.temperature,
            "humidity": data.humidity,
            "pressure": data.pressure,
        }
