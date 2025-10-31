import time
import math
import statistics
import board
import busio
from adafruit_ltr390 import LTR390
from config import SENSORS, READING_TIME, MEASURING_TIME


class LTR390Sensor:
    """LTR390 UV and ambient light sensor with averaging and config integration."""

    def __init__(self):
        uv_conf = SENSORS.get("light_sensor", {})
        if uv_conf.get("working", False):
            print("[LTR390] Skipped (working=False)")
            self.sensor = None
            return

        self.interval_sec = READING_TIME
        self.total_time = MEASURING_TIME

        # Use default I2C pins
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = LTR390(i2c)
        print("[LTR390] Initialized successfully on default I2C bus")

    def _safe_mean(self, values):
        clean = [v for v in values if v is not None and not math.isnan(v)]
        return statistics.mean(clean) if clean else 0.0

    def measure_interval(self):
        """Take a single UV and light measurement."""
        try:
            uv = self.sensor.uvi
            light = self.sensor.light
            return uv, light
        except Exception as e:
            print(f"[LTR390] Read error: {e}")
            return None, None

    def average_values(self):
        """Measure UV and light over total_time and return averaged results."""
        uv_values = []
        light_values = []
        start_time = time.time()

        while time.time() - start_time < self.total_time:
            uv, light = self.measure_interval()
            if uv is not None and light is not None:
                uv_values.append(uv)
                light_values.append(light)
            time.sleep(self.interval_sec)

        avg_uv = self._safe_mean(uv_values)
        avg_light = self._safe_mean(light_values)

        print(f"Average UV index: {avg_uv:.2f}, Light intensity: {avg_light:.2f}")
        return {"uv_index": avg_uv, "light_intensity": avg_light}


# === Example usage ===
if __name__ == "__main__":
    sensor = LTR390Sensor()
    results = sensor.average_values()
    print(results)
