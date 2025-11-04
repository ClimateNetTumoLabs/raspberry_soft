import math
import asyncio
from gpiozero import MCP3008
from config import SENSORS, READING_TIME, MEASURING_TIME


class WindDirectionSensor:
    """Wind vane sensor using MCP3008 ADC, averaging over multiple intervals (async)."""

    def __init__(self):
        wind_conf = SENSORS.get("wind_direction", {})
        if not wind_conf.get("working", False):
            print("[Wind direction] Skipped (working=False)")
            self.adc = None
            return

        self.adc = MCP3008(channel=wind_conf["adc_channel"])
        self.vref = wind_conf["adc_vref"]
        self.tolerance = wind_conf["tolerance"]
        self.interval_sec = READING_TIME  # 30s
        self.total_time = MEASURING_TIME  # 5 min

        self.volts = {
            0.0: 3.84, 22.5: 1.98, 45.0: 2.25, 67.5: 0.41,
            90.0: 0.45, 112.5: 0.32, 135.0: 0.90, 157.5: 0.62,
            180.0: 1.40, 202.5: 1.19, 225.0: 3.08, 247.5: 2.93,
            270.0: 4.62, 292.5: 4.04, 315.0: 4.33, 337.5: 3.43
        }
        self.volt_to_angle = {v: k for k, v in self.volts.items()}

        print("[Wind direction] Initialized")

    def _get_average(self, angles):
        """Compute circular average of angles."""
        sin_sum = sum(math.sin(math.radians(a)) for a in angles)
        cos_sum = sum(math.cos(math.radians(a)) for a in angles)
        avg = math.degrees(math.atan2(sin_sum, cos_sum))
        return avg if avg >= 0 else avg + 360

    def _angle_to_direction(self, angle):
        """Convert angle to compass direction."""
        directions = [
            "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
        ]
        ix = int((angle + 11.25) // 22.5) % 16
        return directions[ix]

    async def measure_interval(self):
        """Non-blocking measurement over one interval."""
        data = []
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < self.interval_sec:
            wind_v = round(self.adc.value * self.vref, 2)
            closest = min(self.volt_to_angle.keys(), key=lambda x: abs(x - wind_v))
            if abs(closest - wind_v) <= self.tolerance:
                data.append(self.volt_to_angle[closest])
            await asyncio.sleep(0.05)  # yield control
        return self._get_average(data) if data else None

    async def average_direction(self):
        """Non-blocking averaging over total_time."""
        readings = []
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < self.total_time:
            interval_angle = await self.measure_interval()
            if interval_angle is not None:
                readings.append(interval_angle)
        if not readings:
            return None, None
        avg_angle = self._get_average(readings)
        direction = self._angle_to_direction(avg_angle)

        #print(f"[Wind direction] Direction = {direction}")
        return direction
