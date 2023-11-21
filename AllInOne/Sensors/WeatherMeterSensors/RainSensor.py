from gpiozero import Button
from config import SENSORS


class Rain:
    def __init__(self, bucket_size=0.2794) -> None:
        sensor_info = SENSORS["rain"]
        
        self.sensor = Button(sensor_info["pin"])
        self.count = 0
        self.bucket_size = bucket_size

    def press(self):
        self.count += 1

    def clear_data(self):
        self.count = 0

    def read_data(self):
        result = self.count * self.bucket_size
        self.count = 0
        return result
