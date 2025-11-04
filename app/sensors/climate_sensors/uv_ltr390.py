import asyncio
import math
import statistics
import board
import busio
from adafruit_ltr390 import LTR390
from config import SENSORS, READING_TIME, MEASURING_TIME

class LTR390Sensor:
    def __init__(self):
        uv_conf = SENSORS.get("light_sensor", {})
        if not uv_conf.get("working", False):
            print("[LTR390] Skipped")
            self.sensor = None
            return

        self.interval_sec = READING_TIME
        self.total_time = MEASURING_TIME

        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = LTR390(i2c)
        print("[LTR390] Initialized")

    def _safe_mean(self, values):
        clean = [v for v in values if v is not None and not math.isnan(v)]
        return statistics.mean(clean) if clean else 0.0

    async def measure_interval(self):
        try:
            return self.sensor.uvi, self.sensor.light
        except:
            return None, None

    async def average_values(self):
        uv_vals, light_vals = [], []
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < self.total_time:
            uv, light = await self.measure_interval()
            if uv is not None:
                uv_vals.append(uv)
                light_vals.append(light)
            await asyncio.sleep(self.interval_sec)

        uv = round(self._safe_mean(uv_vals))
        lux = round(self._safe_mean(light_vals))

        #print(f'[LTR390] uv = {uv}, lux = {lux}')
        return {"uv": uv, "lux": lux}
