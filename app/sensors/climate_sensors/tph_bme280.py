import time
import math
import statistics
from smbus2 import SMBus
import bme280
from config import SENSORS, READING_TIME, MEASURING_TIME


class BME280Sensor:
    """BME280 sensor for temperature, humidity, and pressure with averaging and config support."""

    def __init__(self):
        bme_conf = SENSORS.get("tph_sensor", {})
        if bme_conf.get("working", False):
            print("[BME280] Skipped (working=False)")
            self.sensor = None
            return

        self.port = bme_conf["port"]
        self.address = bme_conf["address"]
        self.interval_sec = READING_TIME     # e.g. 30s
        self.total_time = MEASURING_TIME     # 5 min average

        self.bus = SMBus(self.port)
        self.calibration = bme280.load_calibration_params(self.bus, self.address)
        print(f"[BME280] Initialized on I2C port={self.port}, address={hex(self.address)}")

    def _safe_mean(self, values):
        clean = [v for v in values if v is not None and not math.isnan(v)]
        return statistics.mean(clean) if clean else 0.0

    def measure_interval(self):
        """Read temperature, humidity, and pressure once."""
        try:
            data = bme280.sample(self.bus, self.address, self.calibration)
            return data.temperature, data.humidity, data.pressure
        except Exception as e:
            print(f"[BME280] Read error: {e}")
            return None, None, None

    def average_values(self):
        """Measure for total_time, taking readings every interval_sec, and return averaged results."""
        temps, hums, presses = [], [], []
        start_time = time.time()

        while time.time() - start_time < self.total_time:
            t, h, p = self.measure_interval()
            if t is not None:
                temps.append(t)
                hums.append(h)
                presses.append(p)
            time.sleep(self.interval_sec)

        avg_temp = round(self._safe_mean(temps), 2)
        avg_hum = self._safe_mean(hums)
        avg_press = self._safe_mean(presses)

        print(f"[BME280] Avg T={avg_temp:.2f}°C, H={avg_hum:.2f}%, P={avg_press:.2f}hPa")
        self.bus.close()

        return {"temperature": avg_temp, "humidity": avg_hum, "pressure": avg_press}


# === Example usage ===
if __name__ == "__main__":
    sensor = BME280Sensor()
    result = sensor.average_values()
    print(result)
