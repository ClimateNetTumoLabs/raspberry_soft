import time
from gpiozero import Button
from config import SENSORS, MEASURING_TIME, TRANSMISSION_INTERVAL


class RainSensor:
    """Counts rain bucket tips over a fixed period and calculates rainfall."""

    def __init__(self):
        rain_conf = SENSORS.get("rain", {})
        if not rain_conf.get("working", False):
            print("[Rain sensor] Skipped (working=False)")
            self.sensor = None
            return

        self.pin = rain_conf["pin"]
        self.bucket_size = rain_conf["bucket_size"]     # mm per tip
        self.total_time = MEASURING_TIME                # e.g. 300s (5 min)

        self.sensor = Button(self.pin)
        self.count = 0
        self.sensor.when_pressed = self._on_click

        print(f"[RainSensor] Initialized on GPIO {self.pin}")

    def _on_click(self):
        """Increment counter when the rain gauge tips."""
        self.count += 1

    def measure_interval(self):
        """Count rain tips during total_time seconds."""
        self.count = 0
        start_time = time.monotonic()
        while time.monotonic() - start_time < self.total_time:
            time.sleep(0.1)
        total_tips = self.count
        return total_tips

    def total_rainfall(self):
        """Calculate total rainfall in mm and mm/h equivalent."""
        total_tips = self.measure_interval()
        rainfall_mm = total_tips * self.bucket_size

        print(f"[RainSensor] Tips={total_tips}, Rain={rainfall_mm:.3f}mm")
        return rainfall_mm


if __name__ == "__main__":
    sensor = RainSensor()
    result = sensor.total_rainfall()
    print(result)
