from gpiozero import Button


class WindSpeed:
    """
    A class representing a wind speed sensor that measures wind speed based on rotations within a specified interval.

    Attributes:
        gpio_pin (int): The GPIO pin number connected to the wind speed sensor.
        turn_distance (float): The distance covered by one full rotation of the wind vane.
        sensor (gpiozero.Button): Button object representing the wind speed sensor.
        count (int): Counter for the number of rotations.
    
    Methods:
        press(): Callback function triggered when the wind speed sensor's button is pressed (rotation detected).
        get_data(interval): Calculates and returns the wind speed based on rotations and interval.
        reset(): Resets the rotation count.
    """

    def __init__(self, gpio_pin=5, turn_distance=2.4) -> None:
        """
        Initializes the WindSpeed sensor with specified attributes.

        Args:
            gpio_pin (int, optional): The GPIO pin number connected to the wind speed sensor. Defaults to 5.
            turn_distance (float, optional): The distance covered by one full rotation of the wind vane. Defaults to 2.4.
        """
        self.sensor = Button(gpio_pin)
        self.count = 0
        self.turn_distance = turn_distance
    
    def press(self):
        """
        Callback function triggered when the wind speed sensor's button is pressed (rotation detected).
        It increments the rotation count.
        """
        self.count += 1
    
    def get_data(self, interval):
        """
        Calculates and returns the wind speed based on rotations and interval.

        Args:
            interval (int): The time interval (in seconds) over which rotations are counted.

        Returns:
            float: Calculated wind speed.
        """
        return round((self.count / interval) * self.turn_distance, 2)

    def reset(self):
        """
        Resets the rotation count back to zero.
        """
        self.count = 0
