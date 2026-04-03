from gpiozero import Button
from config import SENSORS
from logger_config import logging
import time

class RainSensor:
    def __init__(self):
        conf = SENSORS["rain"]
        self.working = conf["working"]
        self.rain = Button(conf["pin"])
        self.bucket_size = conf["bucket_size"]
        self.rain.when_pressed = self._increment
        logging.info("[Rain] Initialized")

        self.count = 0
        self.last_time = time.time()

    def _increment(self):
        self.count += 1

    def clear_data(self):
        self.count = 0

    def read_data(self):
        data = None
        if self.working:
            result = self.count * self.bucket_size
            self.clear_data()  # Clear count after reading
            data = round(result, 2)

        return data
