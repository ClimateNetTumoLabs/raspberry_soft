import asyncio
import math
import statistics
from sps30 import SPS30
from config import SENSORS, READING_TIME, MEASURING_TIME

class SPS30Sensor:
    """SPS30 sensor with async warmup and averaging."""

    def __init__(self):
        sps_conf = SENSORS.get("air_pollution_sps30", {})
        if not sps_conf.get("working", False):
            print("[SPS30] Skipped")
            self.sps = None
            return

        self.port = sps_conf["port"]
        self.interval_sec = READING_TIME
        self.total_time = MEASURING_TIME
        self.warmup_time = sps_conf["warmup"]  # seconds
        self.autoclean = sps_conf["autoclean"]
        self.sps = SPS30(self.port)
        print("[SPS30] Initialized")

    def _safe_mean(self, values):
        clean = [v for v in values if v is not None and not math.isnan(v)]
        return statistics.mean(clean) if clean else 0.0

    async def measure_interval(self):
        """Read particulate matter once (non-blocking)."""
        flag = self.sps.read_data_ready_flag()
        if flag and self.sps.read_measured_values() != self.sps.MEASURED_VALUES_ERROR:
            vals = self.sps.dict_values
            return vals["pm1p0"], vals["pm2p5"], vals["pm10p0"]
        return None, None, None

    async def average_values(self):
        """Measure for total_time with async warmup and averaging."""
        if self.sps.read_article_code() == self.sps.ARTICLE_CODE_ERROR:
            raise RuntimeError("ARTICLE CODE CRC ERROR")

        if self.autoclean:
            self.sps.start_fan_cleaning()

        self.sps.start_measurement()
        print(f"[SPS30] Warming up for {self.warmup_time}s")
        await asyncio.sleep(self.warmup_time)  # non-blocking warmup

        pm1_vals, pm25_vals, pm10_vals = [], [], []
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < self.total_time:
            pm1, pm25, pm10 = await self.measure_interval()
            if pm1 is not None:
                pm1_vals.append(pm1)
                pm25_vals.append(pm25)
                pm10_vals.append(pm10)
            await asyncio.sleep(self.interval_sec)

        avg_pm1 = round(self._safe_mean(pm1_vals))
        avg_pm25 = round(self._safe_mean(pm25_vals))
        avg_pm10 = round(self._safe_mean(pm10_vals))

        self.sps.stop_measurement()

        print(f"[SPS30] Avg PM1={avg_pm1}, PM2.5={avg_pm25}, PM10={avg_pm10}")
        return {"pm1": avg_pm1, "pm2_5": avg_pm25, "pm10": avg_pm10}
