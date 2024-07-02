import adafruit_ltr390
import board
import busio
from config import SENSORS
from logger_config import logging


class LightSensor:
    """
    Interface for interacting with the LTR390 light sensor.

    Attributes:
        sensor (adafruit_ltr390.LTR390 or None): Instance of the LTR390 sensor.
        i2c (busio.I2C or None): Instance of the I2C bus.
        sensor_info (dict): Configuration information for the sensor.
        working (bool): Indicates if the sensor is working.
    """

    def __init__(self) -> None:
        """
        Initializes the LightSensor instance.
        """
        self.sensor = None
        self.i2c = None
        self.sensor_info = SENSORS["light_sensor"]
        self.working = self.sensor_info["working"]

        if self.working:
            self.setup_sensor()

    def setup_sensor(self) -> bool:
        """
        Sets up the LTR390 sensor instance.

        Returns:
            bool: True if sensor setup was successful, False otherwise.
        """
        for i in range(3):
            try:
                self.i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = adafruit_ltr390.LTR390(self.i2c)
                break
            except Exception as e:
                logging.error(f"Error occurred during creating object for LTR390 sensor: {e}")

        return self.sensor is not None

    def read_data(self) -> dict:
        """
        Reads light data from the LTR390 sensor.

        Returns:
            dict: Dictionary containing light data (uv and lux).
        """
        data = {"uv": None, "lux": None}

        if self.working:
            if self.sensor is None:
                if not self.setup_sensor():
                    return data

            try:
                uvi = self.sensor.uvi
                lux = self.sensor.lux
            except AttributeError as e:
                logging.error(f"Attribute error while reading LTR390: {e}")
            except Exception as e:
                logging.error(f"Unhandled exception while reading LTR390: {e}", exc_info=True)
            else:
                data["uv"] = round(uvi, 2)
                data["lux"] = round(lux)

        return data
