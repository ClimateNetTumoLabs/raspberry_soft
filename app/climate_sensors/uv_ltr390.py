from base_sensor import BaseSensor
from adafruit_ltr390 import LTR390
import board
import busio


class LTR390Sensor(BaseSensor):
    def __init__(self, config_manager):
        super().__init__(config_manager, "uv_ltr390")
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = LTR390(i2c)

    def _read_sensor(self):
        return {
            "uv_index": self.sensor.uvi,
            "light_intensity": self.sensor.light,
        }
