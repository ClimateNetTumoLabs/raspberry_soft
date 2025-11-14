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
        """Initialize the LTR390 light sensor."""
        for i in range(3):
            try:
                self.i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = adafruit_ltr390.LTR390(self.i2c)
                #self.sensor.resolution = adafruit_ltr390.LTR390.RESOLUTION_20BIT
                #self.sensor.gain = adafruit_ltr390.LTR390.GAIN_18X
                break
            except Exception as e:
                logging.error(f"Error occurred while creating LTR390 object: {e}")

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
                return round(uvs[idx])
            else:
                logging.warning("Current hour not found in UV API response.")

        except requests.exceptions.ConnectionError:
            logging.warning("No internet or DNS failure while fetching UV index — using fallback.")
        except requests.exceptions.Timeout:
            logging.warning("Open-Meteo API request timed out — using fallback.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error while fetching UV index from Open-Meteo: {e}")
        except Exception as e:
            logging.error(f"Unexpected error fetching UV index: {e}", exc_info=True)

        return None

    def read_data(self) -> dict:
        """
        Reads lux from the LTR390 sensor and UV index from the Open-Meteo API.

        Returns:
            dict: Dictionary containing light data (uv and lux).
        """
        data = {"uv": None, "lux": None}

        if self.working:
            if self.sensor is None:
                if not self.setup_sensor():
                    return data

            # Only read LUX (no UV reading from sensor)
            try:
                lux = self.sensor.lux
                data["lux"] = round(lux)
            except (AttributeError, OSError) as e:
                logging.error(f"Error while reading LTR390 lux: {e}")
            except Exception as e:
                logging.error(f"Unhandled exception while reading LTR390 lux: {e}", exc_info=True)

        # Fetch UV only from the API (sensor does not provide UV)
        uv_from_api = self.fetch_uv_from_api()
        if uv_from_api is not None:
            data["uv"] = uv_from_api
        else:
            data["uv"] = None
        return data
