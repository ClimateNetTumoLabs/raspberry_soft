from gpiozero import Button
from config import SENSORS
import time

class RainSensor:
    def __init__(self):
        conf = SENSORS["rain"]
        self.enabled = conf["working"]
        try:
            if self.enabled:
                self.rain = Button(conf["pin"])
                self.bucket_size = conf["bucket_size"]
                self.rain.when_pressed = self._increment
                print("[Rain] Initialized successfully")
            else:
                print("[Rain] Disabled in config")
        except Exception as e:
            print(f"[Rain] Initialization failed: {e}")
            self.connected = False

        self.count = 0
        self.last_time = time.time()

    def _increment(self):
        self.count += 1

    def read_data(self):
        if not self.rain or not self.enabled:
            return {"rain": None}
        try:
            count = self.count
            self.count = 0
            self.last_time = time.time()
            total = count * self.bucket_size
            return round(total, 2)
        except Exception as e:
            print(f"[Rain] Get/reset failed: {e}")
            return {"rain": None}
