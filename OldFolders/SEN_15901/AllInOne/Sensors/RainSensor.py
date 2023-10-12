from gpiozero import Button


class Rain:
    """
    A class representing a rain sensor that detects rain events.

    Attributes:
        gpio_pin (int): The GPIO pin number connected to the rain sensor.
        bucket_size (float): The size of the rain bucket (in mm) for each rain event.
        sensor (gpiozero.Button): Button object representing the rain sensor.
        count (int): Counter for the number of rain events.

    Methods:
        press(): Callback function triggered when the rain sensor's button is pressed (rain event detected).
        get_data(): Calculates and returns the accumulated rain measurement in millimeters.
        reset(): Resets the rain event count.
    """

    def __init__(self, gpio_pin=6, bucket_size=0.2794) -> None:
        """
        Initializes the Rain sensor with the specified GPIO pin and bucket size.

        Args:
            gpio_pin (int, optional): The GPIO pin number connected to the rain sensor. Defaults to 6.
            bucket_size (float, optional): The size of the rain bucket (in mm) for each rain event.
                                           Defaults to 0.2794 mm.
        """
        self.sensor = Button(gpio_pin)
        self.count = 0
        self.bucket_size = bucket_size
    
    def press(self):
        """
        Callback function triggered when the rain sensor's button is pressed (rain event detected).
        It increments the rain event count.
        """
        self.count += 1
    
    def get_data(self):
        """
        Calculates and returns the accumulated rain measurement in millimeters.

        Returns:
            float: Accumulated rain measurement in millimeters.
        """
        return round(self.count * self.bucket_size, 2)
    
    def reset(self):
        """
        Resets the rain event count back to zero.
        """
        self.count = 0
