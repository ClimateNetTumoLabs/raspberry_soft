from gpiozero import Button


class WindSpeed:
    """
    Class for measuring wind speed using an anemometer sensor.

    This class provides methods for measuring wind speed using an anemometer sensor connected to a GPIO pin.

    Args:
        gpio_pin (int): The GPIO pin to which the anemometer sensor is connected (default is 5).
        turn_distance (float): The distance covered by one full turn of the anemometer blades (default is 2.4 meters).

    Attributes:
        sensor (Button): The Button object representing the anemometer sensor.
        count (int): The count of sensor activations.
        turn_distance (float): The distance covered by one full turn of the anemometer blades.

    Methods:
        press(self):
            Increment the count of sensor activations when the anemometer sensor is activated.

        clear_data(self):
            Reset the count of sensor activations to zero.

        read_data(self, interval):
            Calculate and return the wind speed based on the count of sensor activations and the measurement interval,
            and reset the count to zero.

    """

    def __init__(self, gpio_pin=5, turn_distance=2.4):
        """
        Initialize the WindSpeed class.

        This method initializes the WindSpeed class and sets up the GPIO pin, count of sensor activations, and the turn distance.

        Args:
            gpio_pin (int): The GPIO pin to which the anemometer sensor is connected (default is 5).
            turn_distance (float): The distance covered by one full turn of the anemometer blades (default is 2.4 meters).

        Returns:
            None
        """
        self.sensor = Button(gpio_pin)
        self.count = 0
        self.turn_distance = turn_distance

    def press(self):
        """
        Increment the count of sensor activations when the anemometer sensor is activated.

        This method is called when the anemometer sensor is activated (e.g., a full turn of the blades occurs).
        It increments the count of sensor activations.

        Returns:
            None
        """
        self.count += 1

    def clear_data(self):
        """
        Reset the count of sensor activations to zero.

        This method resets the count of sensor activations to zero, effectively clearing the accumulated count.

        Returns:
            None
        """
        self.count = 0
    
    def get_data(self):
        return self.count

    def read_data(self, interval):
        """
        Calculate and return the wind speed based on the count of sensor activations and the measurement interval,
        and reset the count to zero.

        This method calculates the wind speed based on the count of sensor activations and the measurement interval.
        It then resets the count of activations to zero.

        Args:
            interval (float): The time interval in seconds over which the count was measured.

        Returns:
            float: The wind speed in kilometers per hour.
        """
        result = round((self.count / interval) * self.turn_distance, 2)
        self.count = 0
        return result
