from adafruit_ltr390 import LTR390
from config import SENSORS
import busio, board
from logger_config import logging
import datetime, requests

class LTR390Sensor:
    def __init__(self):
        conf = SENSORS["ltr390"]
        self.working = conf["working"]
        self.sensor = None
        self.i2c = None

        if self.working:
            self.setup_sensor()

    def setup_sensor(self):
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = LTR390(self.i2c)
            logging.info("[LTR390] Initialized")
            # self.sensor.resolution = adafruit_ltr390.LTR390.RESOLUTION_20BIT
            # self.sensor.gain = adafruit_ltr390.LTR390.GAIN_18X
        except Exception as e:
            logging.error(f"[LTR390] Error occurred while creating LTR390 object: {e}")
            self.sensor = None
            return False

    def fetch_uv_from_api(self) -> float or None:
        try:
            lat, lon = 40.18, 44.51
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=uv_index&timezone=auto"
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            times = data["hourly"]["time"]
            uvs = data["hourly"]["uv_index"]

            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:00")

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

        if self.working and self.sensor:
            try:
                lux = self.sensor.lux
                data["lux"] = round(lux)
            except (AttributeError, OSError) as e:
                logging.error(f"[LTR390] Error while reading LTR390 lux: {e}")
            except Exception as e:
                logging.error(f"[LTR390] Unhandled exception while reading LTR390 lux: {e}", exc_info=True)

            uv_from_api = self.fetch_uv_from_api()
            if uv_from_api is not None:
                data["uv"] = uv_from_api
            else:
                data["uv"] = None
        return data

if __name__=="__main__":
    uv = LTR390Sensor()
    print(uv.read_data())