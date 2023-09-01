import time
from .RainSensor import Rain
from .WindDirectionSensor import WindDirection
from .WindSpeedSensor import WindSpeed


class WeatherSensors:
    def __init__(self, parse_interval=20):
        self.direction = WindDirection()
        self.speed = WindSpeed()
        self.rain = Rain()

        self.parse_interval = parse_interval

        self.speed.sensor.when_pressed = self.speed.press
        self.rain.sensor.when_pressed = self.rain.press

    def reset_all(self):
        self.speed.reset()
        self.rain.reset()
        self.direction.reset()

    def get_data(self):
        start_time = time.time()
        old_speed_count = 0

        while time.time() - start_time <= self.parse_interval:
            if self.speed.count != old_speed_count:
                old_speed_count = self.speed.count
                self.direction.add_data()

        result = {
            "speed": self.speed.get_data(self.parse_interval),
            "rain": self.rain.get_data(),
            "direction": self.direction.get_data()
        }

        self.reset_all()

        return result