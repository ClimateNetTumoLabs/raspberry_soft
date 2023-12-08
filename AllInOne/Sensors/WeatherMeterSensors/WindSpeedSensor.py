"""
    Module for interacting with a wind speed sensor.

    This module provides a WindSpeed class for reading wind speed data.

    Class Docstring:
    ----------------
    WindSpeed:
        Interacts with a wind speed sensor to read wind speed data.

    Constructor:
        Initializes a WindSpeed object based on the configuration specified in the SENSORS module.

    Class Attributes:
        sensor (Button): An instance of the Button class from the gpiozero library for counting wind speed.
        count (int): Counter for wind speed measurement.
        turn_distance (float): Distance covered by one rotation of the wind speed sensor.

    Methods:
        press(self): Increment the wind speed counter.
        clear_data(self): Reset the wind speed counter to zero.
        get_data(self): Get the current wind speed count.
        read_data(self, interval): Read wind speed data and calculate the wind speed.

    Module Usage:
    -------------
    To use this module, create an instance of the WindSpeed class. Call press() to increment the wind speed counter based on sensor input. Call clear_data() to reset the counter. Call read_data(interval) to get the wind speed calculated over the specified time interval.
"""

from gpiozero import Button
from config import SENSORS


class WindSpeed:
    """
    Interacts with a wind speed sensor to read wind speed data.

    Attributes:
        sensor (Button): An instance of the Button class from the gpiozero library for counting wind speed.
        count (int): Counter for wind speed measurement.
        turn_distance (float): Distance covered by one rotation of the wind speed sensor.
    """

    def __init__(self, turn_distance=2.4) -> None:
        """
        Initializes a WindSpeed object based on the configuration specified in the SENSORS module.
        """
        sensor_info = SENSORS["wind_speed"]

        self.sensor = Button(sensor_info["pin"])
        self.count = 0
        self.turn_distance = turn_distance

    def press(self) -> None:
        """
        Increment the wind speed counter.
        """
        self.count += 1

    def clear_data(self) -> None:
        """
        Reset the wind speed counter to zero.
        """
        self.count = 0

    def get_data(self) -> int:
        """
        Get the current wind speed count.

        Returns:
            int: Current wind speed count.
        """
        return self.count

    def read_data(self, interval: float) -> float:
        """
        Read wind speed data and calculate the wind speed.

        Parameters:
            interval (float): Time interval for calculating wind speed.

        Returns:
            float: Calculated wind speed.
        """
        result = round((self.count / interval) * self.turn_distance, 2)
        self.count = 0
        return result
