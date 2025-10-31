import asyncio
from gpiozero import Button
from config import SENSORS, READING_TIME, MEASURING_TIME

class WindSpeedSensor:
    def __init__(self):
        wind_conf = SENSORS.get("wind_speed", {})
        if not wind_conf.get("working", False):
            print("[Wind speed] Skipped")
            self.sensor = None
            return

        self.sensor = Button(wind_conf["pin"])
        self.sensor.when_pressed = self._on_pulse
        self.coefficient = wind_conf["speed_coefficient"]
        self.interval_sec = READING_TIME
        self.total_time = MEASURING_TIME
        self.pulse_count = 0

        print("[Wind speed] Initialized")
    def _on_pulse(self):
        self.pulse_count += 1

    async def measure_interval(self):
        self.pulse_count = 0
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < self.interval_sec:
            await asyncio.sleep(0.01)
        pulses_per_sec = self.pulse_count / self.interval_sec
        return pulses_per_sec * self.coefficient / 3.6  # km/h -> m/s

    async def average_speed(self):
        readings = []
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < self.total_time:
            val = await self.measure_interval()
            readings.append(val)
        avg_speed = round(sum(readings)/len(readings), 1) if readings else 0

        print(f'[Wind Speed] Avg wind speed = {avg_speed}')
        return avg_speed
