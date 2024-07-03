from config import SENSORS
from gpiozero import Button


class Rain:
    """
    Class to handle rain sensor data collection.

    Attributes:
        working (bool): Indicates if the rain sensor is operational.
        bucket_size (float): Size of the rain bucket (amount of rain per sensor count).
        sensor (gpiozero.Button): Button instance for interfacing with the rain sensor GPIO pin.
        count (int): Counter for the number of times the rain sensor has been triggered.

    Methods:
        press: Increments the count attribute when the rain sensor is triggered.
        clear_data: Resets the count attribute to zero.
        read_data: Reads and returns the calculated amount of rain collected.
    """

    def __init__(self) -> None:
        """
        Initializes the Rain sensor instance.
        """
        sensor_info = SENSORS["rain"]
        self.working = sensor_info['working']
        self.bucket_size = sensor_info['bucket_size']
        self.sensor = Button(sensor_info["pin"])
        self.count = 0

    def press(self) -> None:
        """
        Increment the count attribute when the rain sensor is triggered.
        """
        self.count += 1

    def clear_data(self) -> None:
        """
        Reset the count attribute to zero.
        """
        self.count = 0

    def read_data(self) -> float:
        """
        Read and return the calculated amount of rain collected.

        Returns:
            float: Amount of rain collected based on the count multiplied by the bucket size.
                   Returns None if the sensor is not working.
        """
        if self.working:
            result = self.count * self.bucket_size
            self.clear_data()  # Clear count after reading
            return round(result, 2)
        else:
            return None
