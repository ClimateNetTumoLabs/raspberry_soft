from gpiozero import Button


class Rain:
    def __init__(self, gpio_pin=6, bucket_size=0.2794) -> None:
        self.sensor = Button(gpio_pin)
        self.count = 0
        self.bucket_size = bucket_size
    
    def press(self):
        self.count += 1
    
    def read_data(self):
        result = self.count * self.bucket_size
        self.count = 0
        return result
