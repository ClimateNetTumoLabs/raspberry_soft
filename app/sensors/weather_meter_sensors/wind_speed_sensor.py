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

    def read_data(self, interval: float) -> float:
        """
        Calculates and returns the wind speed based on the rotation count and the specified time interval.

        Args:
            interval (float): Time interval in seconds.

        Returns:
            float: Calculated wind speed in meters per second.
        """
        result = round((self.count / interval) * self.turn_distance, 2)
        self.count = 0
        return result
