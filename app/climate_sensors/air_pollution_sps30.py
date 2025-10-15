from base_sensor import BaseSensor
from sps30 import SPS30

class SPS30Sensor(BaseSensor):
    def __init__(self, config_manager):
        super().__init__(config_manager, "air_pollution_sps30")
        self.sensor = SPS30()
        self.sensor.start_measurement()

    def _read_sensor(self):
        data = self.sensor.read_measured_values()
        if not data:
            return None
        return {
            "pm1": data["pm1"],
            "pm2_5": data["pm2_5"],
            "pm10": data["pm10"],
        }
