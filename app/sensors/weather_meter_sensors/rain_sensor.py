from gpiozero import Button
from config import SENSORS


class Rain:
    """
    Represents a rain sensor for measuring rainfall.

    This class utilizes a GPIO button input to detect rain events. Each rain event increments a count, and the total
    rainfall is calculated based on the count and the size of the rain bucket.

    Args:
        bucket_size (float, optional): The size of the rain bucket in millimeters. Defaults to 0.2794.

    Attributes:
        sensor (Button): GPIO button input connected to the rain sensor.
        count (int): The count of rain events.
        bucket_size (float): The size of the rain bucket in millimeters.

    Methods:
        press() -> None: Increments the rain count when a rain event is detected.
        clear_data() -> None: Resets the rain count to zero.
        read_data() -> float: Reads the accumulated rainfall data and resets the count to zero.

    """

    def __init__(self, bucket_size=0.2794) -> None:
        """
        Initializes the Rain object.

        Creates a GPIO button input instance connected to the rain sensor and initializes the rain count and bucket
        size.

        Args:
            bucket_size (float, optional): The size of the rain bucket in millimeters. Defaults to 0.2794.
        """
        sensor_info = SENSORS["rain"]
        self.sensor = Button(sensor_info["pin"])
        self.count = 0
        self.bucket_size = bucket_size

    def press(self) -> None:
        """
        Registers a rain event.

        Increments the rain count when a rain event is detected by the sensor.
        """
        self.count += 1

    def clear_data(self) -> None:
        """
        Clears accumulated rainfall data.

        Resets the rain count to zero.
        """
        self.count = 0

    def read_data(self) -> float:
        """
        Reads the accumulated rainfall data.

        Calculates and returns the total rainfall based on the count of rain events and the size of the rain bucket.
        Resets the rain count to zero after reading.

        Returns:
            float: The accumulated rainfall in millimeters.
        """
        result = self.count * self.bucket_size
        self.count = 0
        return result
