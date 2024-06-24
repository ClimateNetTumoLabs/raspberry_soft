import math

from config import SENSORS
from gpiozero import Button


class WindSpeed:
    """
    Represents a wind speed sensor.

    This class tracks the number of rotations of a wind speed sensor's cup assembly within a specified time interval
    to calculate wind speed.

    Args:
        turn_distance (float, optional): Distance traveled by each rotation of the wind speed sensor's cups.
            Defaults to 2.4 meters.

    Attributes:
        sensor (Button): Button instance representing the wind speed sensor.
        count (int): Number of rotations counted by the sensor.
        turn_distance (float): Distance traveled by each rotation of the wind speed sensor's cups.

    Methods:
        press() -> None: Increments the rotation count when the sensor's button is pressed.
        clear_data() -> None: Resets the rotation count to zero.
        get_data() -> int: Returns the current rotation count.
        read_data(interval: float) -> float: Calculates and returns the wind speed based on the rotation count
            and the specified time interval.

    """

    def __init__(self, turn_distance=2.4) -> None:
        """
        Initializes the WindSpeed object.

        Args:
            turn_distance (float, optional): Distance traveled by each rotation of the wind speed sensor's cups.
                Defaults to 2.4 meters.
        """
        sensor_info = SENSORS["wind_speed"]
        self.sensor = Button(sensor_info["pin"])
        self.count = 0
        self.turn_distance = turn_distance

    def press(self) -> None:
        """
        Increments the rotation count when the sensor's button is pressed.
        """
        self.count += 1

    def clear_data(self) -> None:
        """
        Resets the rotation count to zero.
        """
        self.count = 0

    def get_data(self) -> int:
        """
        Returns the current rotation count.

        Returns:
            int: Current rotation count.
        """
        return self.count

    def convert_speed_to_kmh(self, speed_cm_s: float) -> float:
        """
        Converts speed from centimeters per second to kilometers per hour.

        Args:
            speed_cm_s (float): Speed in centimeters per second.

        Returns:
            float: Speed in kilometers per hour.
        """
        speed_m_per_sec = speed / 100
        speed_km_per_hour = speed_m_per_sec * 3.6

        return speed_km_per_hour

    def read_data(self, interval: float) -> float:
        """
        Calculates and returns the wind speed based on the rotation count and the specified time interval.

        Args:
            interval (float): Time interval in seconds.

        Returns:
            float: Calculated wind speed in kilometer per hour.
        """
        # Constants
        radius_cm = 7
        circumference_cm = 2 * math.pi * radius_cm

        # Calculate rotations and distance
        rotations = self.count / 2
        dist_cm = circumference_cm * rotations

        # Convert to km and calculate speed
        speed_cms = dist_cm / interval
        speed_kmph = self.convert_speed_to_kmh(speed_cms)

        self.count = 0
        return speed_kmph
