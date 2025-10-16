from ..base_sensor import BaseSensor
from sps30 import SPS30
import time

class SPS30Sensor(BaseSensor):
    def __init__(self, config_manager):
        super().__init__(config_manager, "air_pollution_sps30")
        if not self.enabled:
            return

        self.sensor = self._init_sensor()

    def _init_sensor(self):
        cfg = self.config.get_sensor_config(self.name)
        port = cfg.get("port", 1)
        warmup_time = cfg.get("warmup_time", 5)

        sensor = SPS30(port)
        article_code = sensor.read_article_code()
        if article_code == sensor.ARTICLE_CODE_ERROR:
            raise RuntimeError("SPS30: ARTICLE CODE CRC ERROR (check wiring/I2C)")

        sensor.start_measurement()
        time.sleep(warmup_time)
        return sensor

    def _read_sensor(self):
        if not self.enabled:
            return None

        if not self.sensor.read_data_ready_flag():
            return None
        if self.sensor.read_measured_values() == self.sensor.MEASURED_VALUES_ERROR:
            return None

        values = self.sensor.dict_values
        return {
            "pm1": values.get("pm1p0"),
            "pm2_5": values.get("pm2p5"),
            "pm10": values.get("pm10p0"),
        }

    def stop(self):
        if not self.enabled:
            return
        try:
            self.sensor.stop_measurement()
        except Exception:
            pass
