import asyncio
import math
import statistics
from smbus2 import SMBus
import bme280
from config import SENSORS, READING_TIME, MEASURING_TIME

class BME280Sensor:
    def __init__(self):
        bme_conf = SENSORS.get("tph_sensor", {})
        if not bme_conf.get("working", False):
            print("[BME280] Skipped")
            self.bus = None
            return

        self.port = bme_conf["port"]
        self.address = bme_conf["address"]
        self.interval_sec = READING_TIME
        self.total_time = MEASURING_TIME

        self.bus = SMBus(self.port)
        self.calibration = bme280.load_calibration_params(self.bus, self.address)
        print("[BME280] Initialized")

    def _safe_mean(self, values):
        clean = [v for v in values if v is not None and not math.isnan(v)]
        return statistics.mean(clean) if clean else 0.0

    async def measure_interval(self):
        try:
            data = bme280.sample(self.bus, self.address, self.calibration)
            return data.temperature, data.humidity, data.pressure
        except:
            return None, None, None

    async def average_values(self):
        temps, hums, presses = [], [], []
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < self.total_time:
            t, h, p = await self.measure_interval()
            if t is not None:
                temps.append(t)
                hums.append(h)
                presses.append(p)
            await asyncio.sleep(self.interval_sec)

        avg_temp = round(self._safe_mean(temps), 2)
        avg_hum = round(self._safe_mean(hums), 2)
        avg_press = round(self._safe_mean(presses), 2)
        self.bus.close()

        print(f"[BME280] Avg temp={avg_temp}, hum={avg_hum}, pres={avg_press}")

        return {"temperature": avg_temp, "humidity": avg_hum, "pressure": avg_press}
