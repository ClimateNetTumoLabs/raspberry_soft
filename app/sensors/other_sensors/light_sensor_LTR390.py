import adafruit_ltr390
import board
import busio
import requests
from datetime import datetime
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
        self.sensor = None
        self.i2c = None
        self.sensor_info = SENSORS["light_sensor"]
        self.working = self.sensor_info["working"]

        if self.working:
            self.setup_sensor()

    def setup_sensor(self) -> bool:
        for i in range(3):
            try:
                self.i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = adafruit_ltr390.LTR390(self.i2c)
                self.sensor.resolution = adafruit_ltr390.LTR390.RESOLUTION_20BIT
                self.sensor.gain = adafruit_ltr390.LTR390.GAIN_18X
                break
            except Exception as e:
                logging.error(f"Error occurred during creating object for LTR390 sensor: {e}")

        return self.sensor is not None

    def fetch_uv_from_api(self) -> float or None:
        """
        Fetches UV index from Open-Meteo API using current hour.

        Returns:
            float or None: UV index rounded to 2 decimal places, or None if fetch fails.
        """
        try:
            lat, lon = 40.18, 44.51
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=uv_index&timezone=auto"
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            times = data["hourly"]["time"]
            uvs = data["hourly"]["uv_index"]

            now = datetime.now().strftime("%Y-%m-%dT%H:00")

            if now in times:
                idx = times.index(now)
                return round(uvs[idx], 2)
            else:
                logging.warning("Current hour not found in UV API response.")
        except Exception as e:
            logging.error(f"Error fetching UV index from Open-Meteo: {e}", exc_info=True)
        return None

    def read_data(self) -> dict:
        """
        Reads lux from the LTR390 sensor and UV index from Open-Meteo.

        Returns:
            dict: Dictionary containing light data (uv and lux).
        """
        data = {"uv": None, "lux": None}

        if self.working:
            if self.sensor is None:
                if not self.setup_sensor():
                    return data

            try:
                lux = self.sensor.lux
                data["lux"] = round(lux)
            except AttributeError as e:
                logging.error(f"Attribute error while reading LTR390: {e}")
            except OSError as e:
                logging.error(f"OS error while reading LTR390: {e}")
            except Exception as e:
                logging.error(f"Unhandled exception while reading LTR390: {e}", exc_info=True)

        # Always try to fetch UV index from API
        data["uv"] = self.fetch_uv_from_api()

        return data

