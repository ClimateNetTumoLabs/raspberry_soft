from gpiozero import Button
from config import SENSORS


class WindSpeed:
    def __init__(self, turn_distance=2.4):
        sensor_info = SENSORS["wind_speed"]

        self.sensor = Button(sensor_info["pin"])
        self.count = 0
        self.turn_distance = turn_distance

    def press(self):
        self.count += 1

    def clear_data(self):
        self.count = 0
    
    def get_data(self):
        return self.count

    def read_data(self, interval):
        result = round((self.count / interval) * self.turn_distance, 2)
        self.count = 0
        return result
