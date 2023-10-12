import time
from gpiozero import Button


class RainSensor(object):
    """
    A class representing a rain sensor using a tipping bucket mechanism.

    Attributes:
        gpio_pin (int): The GPIO pin number connected to the rain sensor.
        bucket_size (float): The amount of rainfall (in millimeters) collected per bucket tip.
        interval (int): The time interval (in seconds) for measuring rainfall.

    Methods:
        bucket_tipped(): Callback function triggered when the tipping bucket is tipped (rain is detected).
        get_data(): Gets the accumulated rainfall data over the specified interval.
    """

    def __init__(self, gpio_pin=6, bucket_size=0.2794, interval=10):
        """
        Initializes the RainSensor with the specified GPIO pin, bucket size, and interval.

        Args:
            gpio_pin (int, optional): The GPIO pin number connected to the rain sensor. Defaults to 6.
            bucket_size (float, optional): The amount of rainfall (in millimeters) collected per bucket tip.
                                           Defaults to 0.2794 mm (corresponding to 0.011 inches).
            interval (int, optional): The time interval (in seconds) for measuring rainfall. Defaults to 10 seconds.
        """
        self.gpio_pin = gpio_pin
        self.rain_sensor = Button(gpio_pin)
        self.bucket_size = bucket_size
        self.interval = interval
        self.count = 0
        self.rain_sensor.when_pressed = self.bucket_tipped

    def bucket_tipped(self):
        """
        Callback function triggered when the tipping bucket is tipped (rain is detected).
        It increments the rain count by 1.
        """
        self.count += 1

    def get_data(self):
        """
        Gets the accumulated rainfall data over the specified interval.

        Returns:
            str: A string representing the accumulated rainfall in millimeters (mm) over the interval.
        """
        time.sleep(self.interval)
        rainfall_mm = self.count * self.bucket_size
        self.count = 0
        return rainfall_mm


if __name__ == "__main__":
    rain_sensor = RainSensor()
    while True:
        print(f"{round(rain_sensor.get_data(), 2)}mm")

