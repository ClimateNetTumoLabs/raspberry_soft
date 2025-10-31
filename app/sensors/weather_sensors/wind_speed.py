import time
from gpiozero import Button
from config import SENSORS, READING_TIME, MEASURING_TIME

class WindSpeedSensor:
    """Wind speed sensor with averaging over configured interval."""

    def __init__(self):
        wind_conf = SENSORS.get("wind_speed", {})
        if not wind_conf.get("working", False):
            print("[Wind speed] Skipped (working=False)")
            self.sensor = None
            return

        pin = wind_conf.get["gpio_pin"]
        if pin is None:
            raise ValueError("Wind speed sensor GPIO pin not defined in config.")
        self.sensor = Button(pin)
        self.sensor.when_pressed = self._on_pulse

        self.coefficient = wind_conf["speed_coefficient"]
        self.interval_sec = READING_TIME     # measuring interval
        self.total_time = MEASURING_TIME     # total averaging time (5 min)
        self.pulse_count = 0

    def _on_pulse(self):
        self.pulse_count += 1

    def measure_interval(self):
        """Measure wind speed over the configured interval (seconds)."""
        self.pulse_count = 0
        start_time = time.time()
        while time.time() - start_time < self.interval_sec:
            time.sleep(0.01)
        pulses_per_sec = self.pulse_count / self.interval_sec
        return pulses_per_sec * self.coefficient  # returns km/h

    def average_speed(self):
        """Measure wind speed over the configured total_time and return averaged m/s."""
        readings = []
        start_time = time.time()
        while time.time() - start_time < self.total_time:
            speed_kmh = self.measure_interval()
            speed_m_s = speed_kmh / 3.6
            readings.append(speed_m_s)
        avg_speed = sum(readings) / len(readings) if readings else 0.0
        return avg_speed


# === EXAMPLE USAGE ===
if __name__ == "__main__":
    ws_sensor = WindSpeedSensor()
    avg_speed = ws_sensor.average_speed()
    print(f"5-minute average wind speed: {avg_speed:.2f} m/s")
