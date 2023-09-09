import time
import logging
from .RainSensor import Rain
from .WindDirectionSensor import WindDirection
from .WindSpeedSensor import WindSpeed


logging.basicConfig(filename='parsing.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
    
    def get_direction_label(self, angles):
        return self.direction.get_direction_label(sum(angles) / len(angles))

    def read_data(self):
        try:
            start_time = time.time()
            old_speed_count = 0

            while time.time() - start_time <= self.parse_interval:
                if self.speed.count != old_speed_count:
                    old_speed_count = self.speed.count
                    self.direction.add_data()

            result = {
                "speed": self.speed.get_data(time.time() - start_time),
                "rain": self.rain.get_data(),
                "direction": self.direction.get_data()
            }

            self.reset_all()

            return result
        except Exception as e:
            logging.error(f"Error occurred during reading data from WeatherMeter Sensor: {str(e)}", exc_info=True)
            self.reset_all()

            return {
                "speed": None,
                "rain": None,
                "direction": None
            }