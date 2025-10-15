from base_sensor import BaseSensor
from sps30 import SPS30
import time


class SPS30Sensor(BaseSensor):
    """SPS30 particulate matter sensor class using smbus2 and BaseSensor structure."""

    def __init__(self, config_manager):
        super().__init__(config_manager, "air_pollution_sps30")

        # Initialize I2C connection on bus 1
        self.port = 1
        self.sensor = SPS30(self.port)

        # Verify communication
        article_code = self.sensor.read_article_code()
        if article_code == self.sensor.ARTICLE_CODE_ERROR:
            raise RuntimeError("SPS30: ARTICLE CODE CRC ERROR (check wiring/I2C)")

        # Start continuous measurement
        self.sensor.start_measurement()
        time.sleep(5)  # warm-up period before first read

    def _read_sensor(self):
        """Read particulate matter values from SPS30 sensor."""
        # Check data ready flag
        if not self.sensor.read_data_ready_flag():
            return None

        # Read measured values
        if self.sensor.read_measured_values() == self.sensor.MEASURED_VALUES_ERROR:
            return None

        # Extract valid readings from sensor dictionary
        values = self.sensor.dict_values

        return {
            "pm1": values.get("pm1p0"),
            "pm2_5": values.get("pm2p5"),
            "pm10": values.get("pm10p0"),
        }

    def stop(self):
        """Stop measurement gracefully."""
        try:
            self.sensor.stop_measurement()
        except Exception:
            pass
