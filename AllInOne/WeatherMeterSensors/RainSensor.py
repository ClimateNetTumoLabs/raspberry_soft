from gpiozero import Button


class Rain:
    def __init__(self, gpio_pin=6, bucket_size=0.2794) -> None:
        self.sensor = Button(gpio_pin)
        self.count = 0
        self.bucket_size = bucket_size
    
    def press(self):
        self.count += 1
    
    def get_data(self, interval):
        return round(((self.count * self.bucket_size) / interval) * 3600, 2)
    
    def reset(self):
        self.count = 0
