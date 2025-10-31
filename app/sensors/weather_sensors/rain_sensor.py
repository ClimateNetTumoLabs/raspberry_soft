import asyncio
from gpiozero import Button
from config import SENSORS, MEASURING_TIME


class RainSensor:
    """Counts rain bucket tips asynchronously."""

    def __init__(self):
        rain_conf = SENSORS.get("rain", {})
        if not rain_conf.get("working", False):
            print("[Rain sensor] Skipped (working=False)")
            self.sensor = None
            return

        self.pin = rain_conf["pin"]
        self.bucket_size = rain_conf["bucket_size"]
        self.total_time = MEASURING_TIME

        self.sensor = Button(self.pin)
        self.count = 0
        self.sensor.when_pressed = self._on_click

        print("[RainSensor] Initialized")

    def _on_click(self):
        self.count += 1

    async def measure_interval(self):
        """Non-blocking measurement for total_time."""
        self.count = 0
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < self.total_time:
            await asyncio.sleep(0.1)  # yield control
        return self.count

    async def total_rainfall(self):
        """Return total rainfall in mm asynchronously."""
        total_tips = await self.measure_interval()
        rainfall_mm = round(total_tips * self.bucket_size, 2)
        print(f"[RainSensor] Tips={total_tips}, Rain={rainfall_mm:.3f}mm")

        return rainfall_mm
