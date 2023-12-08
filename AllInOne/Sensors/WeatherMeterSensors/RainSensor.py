"""
    Module for interacting with a rain sensor.

    This module provides a Rain class for reading data from a rain sensor.

    Class Docstring:
    ----------------
    Rain:
        Interacts with a rain sensor to measure the amount of rainfall.

    Constructor:
        Initializes a Rain object based on the configuration specified in the SENSORS module.

    Class Attributes:
        sensor: (Button): An instance of the Button class from the gpiozero library for rain sensor input.
        count (int): Count of rain sensor activations.
        bucket_size (float): Size of the rain sensor bucket in millimeters.

    Methods:
        press(self): Increment the count when the rain sensor is activated.
        clear_data(self): Reset the count to zero.
        read_data(self): Calculate and return the total amount of rainfall based on the count and bucket size.

    Module Usage:
    -------------
    To use this module, create an instance of the Rain class. Use the press() method to increment the count when the rain sensor is activated.
    Call read_data() to get the total amount of rainfall, and use clear_data() to reset the count.
"""

from gpiozero import Button
from config import SENSORS


class Rain:
    """
    Interacts with a rain sensor to measure the amount of rainfall.

    Attributes:
        sensor: (Button): An instance of the Button class from the gpiozero library for rain sensor input.
        count (int): Count of rain sensor activations.
        bucket_size (float): Size of the rain sensor bucket in millimeters.
    """

    def __init__(self, bucket_size=0.2794) -> None:
        """
        Initializes a Rain object based on the configuration specified in the SENSORS module.
        """
        sensor_info = SENSORS["rain"]

        self.sensor = Button(sensor_info["pin"])
        self.count = 0
        self.bucket_size = bucket_size

    def press(self) -> None:
        """
        Increment the count when the rain sensor is activated.
        """
        self.count += 1

    def clear_data(self) -> None:
        """
        Reset the count to zero.
        """
        self.count = 0

    def read_data(self) -> float:
        """
        Calculate and return the total amount of rainfall based on the count and bucket size.

        Returns:
            float: The total amount of rainfall in millimeters.
        """
        result = self.count * self.bucket_size
        self.count = 0
        return result
