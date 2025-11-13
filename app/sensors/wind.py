from gpiozero import Button, MCP3008
from config import SENSORS
import time

class WindSpeedSensor:
    """Wind Speed Sensor — counts pulses from an anemometer and converts to speed."""

    def __init__(self):
        conf = SENSORS["speed"]
        self.enabled = conf["working"]
        try:
            if self.enabled:
                self.speed = Button(conf["pin"])
                self.speed.when_pressed = self._increment
                self.count = 0
                self.last_time = time.time()
                print("[Wind speed] Initialized")
            else:
                print("[Wind speed] Disabled in config")
        except Exception as e:
            print(f"[Wind speed] Initialization failed: {e}")

    def _increment(self):
        self.count += 1

    def read_data(self):
        """Return wind speed in m/s (None if disabled or error)."""
        if not self.speed or not self.enabled:
            return {"speed": None}
        try:
            now = time.time()
            elapsed = now - self.last_time
            # Capture count atomically
            current_count = self.count
            self.count = 0
            self.last_time = now

            # Calculate speed (example calibration factor)
            speed_kmh = (current_count / elapsed) * 2.4  # km/h
            speed_m_s = speed_kmh / 3.6  # convert to m/s
            return round(speed_m_s, 2)
        except Exception as e:
            print(f"[Wind speed] Read failed: {e}")
            return {"speed": None}


# ------------------------------
# Wind Direction Sensor
# ------------------------------
class WindDirectionSensor:
    """Wind Direction Sensor — reads voltage from MCP3008 and returns compass direction."""

    def __init__(self):
        conf = SENSORS["direction"]
        self.enabled = conf["working"]
        try:
            if self.enabled:
                self.adc = MCP3008(channel=conf["adc_channel"])
                self.vref = conf["adc_vref"]
                self.tolerance = conf["tolerance"]
                self.volts = {
                    0.0: 3.84, 22.5: 1.98, 45.0: 2.25, 67.5: 0.41,
                    90.0: 0.45, 112.5: 0.32, 135.0: 0.90, 157.5: 0.62,
                    180.0: 1.40, 202.5: 1.19, 225.0: 3.08, 247.5: 2.93,
                    270.0: 4.62, 292.5: 4.04, 315.0: 4.33, 337.5: 3.43
                }
                self.volt_to_angle = {v: k for k, v in self.volts.items()}
                print("[Wind direction] Initialized")
            else:
                print("[Wind direction] Disabled in config")
        except Exception as e:
            print(f"[Wind direction] Initialization failed: {e}")
            self.adc = None

    def _angle_to_direction(self, angle: float) -> str:
        """Convert angle (0–360) to compass direction (N, NNE, NE, etc.)."""
        directions = [
            "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
        ]
        ix = int((angle + 11.25) // 22.5) % 16
        return directions[ix]

    def read_data(self):
        """Take one wind direction reading and return compass direction."""
        if not self.adc:
            return {"direction": None}

        try:
            voltage = round(self.adc.value * self.vref, 2)
            closest_voltage = min(self.volt_to_angle.keys(), key=lambda x: abs(x - voltage))
            if abs(closest_voltage - voltage) > self.tolerance:
                print(f"[Wind direction] Unstable reading: {voltage:.2f}V (no match)")
                return None

            angle = self.volt_to_angle[closest_voltage]
            direction = self._angle_to_direction(angle)
            return direction
        except Exception as e:
            print(f"[Wind direction] Read failed: {e}")
            return None

if __name__=="__main__":
    ws = WindSpeedSensor()
    wd = WindDirectionSensor()

    print(f"Wind speed is {ws.read_data()}")
    print(f"Wind direction is {wd.read_data()}")
