from gpiozero import Button


class Rain:
    """
    Class for measuring rainfall using a rain gauge sensor.

    This class provides methods for measuring rainfall using a rain gauge sensor connected to a GPIO pin.

    Args:
        gpio_pin (int): The GPIO pin to which the rain gauge sensor is connected (default is 6).
        bucket_size (float): The size of the rain gauge bucket in millimeters per tip (default is 0.2794).

    Attributes:
        sensor (Button): The Button object representing the rain gauge sensor.
        count (int): The count of tips or activations of the rain gauge sensor.
        bucket_size (float): The size of the rain gauge bucket in millimeters per tip.

    Methods:
        press(self):
            Increment the tip count when the rain gauge sensor is activated.

        clear_data(self):
            Reset the tip count to zero.

        read_data(self):
            Calculate and return the accumulated rainfall based on the tip count and bucket size,
            and reset the tip count to zero.

    """

    def __init__(self, gpio_pin=6, bucket_size=0.2794) -> None:
        """
        Initialize the Rain class.

        This method initializes the Rain class and sets up the GPIO pin, count of tips, and the bucket size.

        Args:
            gpio_pin (int): The GPIO pin to which the rain gauge sensor is connected (default is 6).
            bucket_size (float): The size of the rain gauge bucket in millimeters per tip (default is 0.2794).

        Returns:
            None
        """

        self.sensor = Button(gpio_pin)
        self.count = 0
        self.bucket_size = bucket_size

    def press(self):
        """
        Increment the tip count when the rain gauge sensor is activated.

        This method is called when the rain gauge sensor is activated (e.g., a tip occurs). It increments
        the count of tips.

        Returns:
            None
        """

        self.count += 1

    def clear_data(self):
        """
        Reset the tip count to zero.

        This method resets the count of tips to zero, effectively clearing the accumulated tip count.

        Returns:
            None
        """

        self.count = 0

    def read_data(self):
        """
        Calculate and return the accumulated rainfall based on the tip count and bucket size,
        and reset the tip count to zero.

        This method calculates the accumulated rainfall based on the tip count and the size of the
        rain gauge bucket. It then resets the tip count to zero.

        Returns:
            float: The accumulated rainfall in millimeters.
        """

        result = self.count * self.bucket_size
        self.count = 0
        return result
