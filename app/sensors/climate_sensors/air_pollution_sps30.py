import time
import math
import statistics
from sps30 import SPS30
from config import SENSORS, READING_TIME, MEASURING_TIME


class SPS30Sensor:
    """SPS30 particulate matter sensor with interval measurements and averaging."""

    def __init__(self):
        sps_conf = SENSORS.get("air_pollution_sps30", {})
        if sps_conf.get("working", False):
            print("[SPS30] Skipped (working=False)")
            self.sensor = None
            return

        self.port = sps_conf["port"]
        self.interval_sec = READING_TIME      # e.g. 30s
        self.total_time = MEASURING_TIME      # 5 min average

        self.sps = SPS30(self.port)
        print(f"[SPS30] Initialized on I2C bus {self.port}")

    def _safe_mean(self, values):
        clean = [v for v in values if v is not None and not math.isnan(v)]
        return statistics.mean(clean) if clean else 0.0

    def measure_interval(self):
        """Read particulate matter values once."""
        flag = self.sps.read_data_ready_flag()
        if flag and self.sps.read_measured_values() != self.sps.MEASURED_VALUES_ERROR:
            vals = self.sps.dict_values
            return vals["pm1p0"], vals["pm2p5"], vals["pm10p0"]
        return None, None, None

    def average_values(self):
        """Warm up, measure for total_time, and return averaged particulate values."""
        if self.sps.read_article_code() == self.sps.ARTICLE_CODE_ERROR:
            raise RuntimeError("ARTICLE CODE CRC ERROR")

        self.sps.start_fan_cleaning()
        self.sps.start_measurement()
        time.sleep(30)  # warm-up

        pm1_vals, pm25_vals, pm10_vals = [], [], []
        start_time = time.time()

        while time.time() - start_time < self.total_time:
            pm1, pm25, pm10 = self.measure_interval()
            if pm1 is not None:
                pm1_vals.append(pm1)
                pm25_vals.append(pm25)
                pm10_vals.append(pm10)
            time.sleep(self.interval_sec)

        avg_pm1 = self._safe_mean(pm1_vals)
        avg_pm25 = self._safe_mean(pm25_vals)
        avg_pm10 = self._safe_mean(pm10_vals)

        print(f"[SPS30] Avg PM1.0={avg_pm1:.2f} µg/m³, PM2.5={avg_pm25:.2f} µg/m³, PM10={avg_pm10:.2f} µg/m³")
        self.sps.stop_measurement()

        return {"pm1p0": avg_pm1, "pm2p5": avg_pm25, "pm10p0": avg_pm10}


# === Example usage ===
if __name__ == "__main__":
    sensor = SPS30Sensor()
    result = sensor.average_values()
    print(result)
