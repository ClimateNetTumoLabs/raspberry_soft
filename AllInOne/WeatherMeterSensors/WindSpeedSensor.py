from gpiozero import Button


class WindSpeed:
    def __init__(self, gpio_pin=5, turn_distance=2.4):
        self.sensor = Button(gpio_pin)
        self.count = 0
        self.turn_distance = turn_distance
    
    def press(self):
        self.count += 1
    
    def read_data(self, interval):
        result = round((self.count / interval) * self.turn_distance, 2)
        self.count = 0
        return result
