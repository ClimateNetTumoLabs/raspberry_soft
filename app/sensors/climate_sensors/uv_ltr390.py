from ..base_sensor import BaseSensor
from adafruit_ltr390 import LTR390
import board
import busio

class LTR390Sensor(BaseSensor):
    def __init__(self, config_manager):
        super().__init__(config_manager, "uv_ltr390")
        if not self.enabled:
            return

        self.sensor = self._init_sensor()

    def _init_sensor(self):
        cfg = self.config.get_sensor_config(self.name)
        scl_pin_name = cfg.get("scl", "SCL")
        sda_pin_name = cfg.get("sda", "SDA")
        address = cfg.get("address", 0x53)

        scl_pin = getattr(board, scl_pin_name)
        sda_pin = getattr(board, sda_pin_name)
        i2c = busio.I2C(scl_pin, sda_pin)
        return LTR390(i2c, address=address)

    def _read_sensor(self):
        if not self.enabled:
            return None

        return {
            "uv_index": self.sensor.uvi,
            "light_intensity": self.sensor.light,
        }
