import math

from config import SENSORS
from gpiozero import Button
from logger_config import logging


class WindSpeed:
    """
    Class to calculate wind speed based on rotations detected by a sensor.

    Attributes:
        turn_distance (float): Distance per rotation (default is 2.4 cm).
        working (bool): Flag indicating if the sensor is operational.
        sensor (gpiozero.Button): Button sensor instance.
        count (int): Rotation count.

    Methods:
        press(): Increments the rotation count.
        clear_data(): Resets the rotation count to zero.
        get_data(): Returns the current rotation count.
        convert_speed_to_kmh(speed_cm_s: float) -> float: Converts speed from cm/s to km/h.
        read_data(interval: float): Calculates wind speed in km/h based on rotations detected within a specified interval.
    """

    def __init__(self, turn_distance=2.4) -> None:
        """
        Initializes the WindSpeed sensor instance.

        Args:
            turn_distance (float): Distance per rotation in centimeters (default is 2.4 cm).
        """
        sensor_info = SENSORS["wind_speed"]
        self.working = sensor_info["working"]
        self.sensor = Button(sensor_info["pin"])
        self.count = 0
        self.turn_distance = turn_distance

    def press(self) -> None:
        """
        Increments the rotation count.
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
        Converts speed from cm/s to km/h.

        Args:
            speed_cm_s (float): Speed in centimeters per second.

        Returns:
            float: Speed converted to kilometers per hour.
        """
        # 1 cm/sec is equal to 0.036 km/hour
        speed_km_hour = speed_cm_s * 0.036
        return speed_km_hour

    def read_data(self, interval: float):
        """
        Calculates wind speed in km/h based on rotations detected within a specified interval.

        Args:
            interval (float): Time interval in seconds.

        Returns:
            float: Calculated wind speed in km/h.
        """
        data = None

        if self.working:
            try:
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

                data = round(speed_kmph, 2)

            except Exception as e:
                logging.error(f"Error occurred during reading WindSpeed: {e}", exc_info=True)

        return data
