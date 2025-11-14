from sps30 import SPS30
from time import sleep
from config import SENSORS
from logger_config import logging


class AirQualitySensor:
    """
    Interface for interacting with the SPS30 air quality sensor (I2C version).
    """

    def __init__(self) -> None:
        self.sensor = None
        self.sensor_info = SENSORS["air_quality_sensor"]
        self.working = self.sensor_info["working"]

        if self.working:
            self.setup_sensor()

    def setup_sensor(self) -> bool:
        """
        Sets up the SPS30 sensor instance.
        """
        try:
            bus = self.sensor_info.get("bus", 1)
            self.sensor = SPS30(bus)

            # Verify communication
            if self.sensor.read_article_code() == self.sensor.ARTICLE_CODE_ERROR:
                raise RuntimeError("ARTICLE CODE CRC ERROR")

            logging.info("SPS30 (I2C) initialized successfully.")
            return True

        except Exception as e:
            logging.error(f"Error occurred during SPS30 I2C setup: {e}", exc_info=True)
            self.sensor = None
            return False

    def enable_auto_cleaning(self, interval_seconds=604800):
        """
        Enable auto fan cleaning (default = 1 week).
        """
        try:
            self.sensor.set_fan_auto_cleaning_interval(interval_seconds)
            logging.info(f"SPS30 auto cleaning interval set to {interval_seconds} seconds")
        except Exception as e:
            logging.error(f"Failed to set auto cleaning interval: {e}")

    def start(self) -> None:
        """
        Starts measurement and enables auto cleaning.
        """
        if not self.sensor:
            return

        try:
            # Set weekly auto-cleaning first
            self.enable_auto_cleaning()

            self.sensor.start_measurement()
            sleep(30)  # warm-up
        except Exception as e:
            logging.error(f"Error during SPS30 start: {e}", exc_info=True)

    def stop(self) -> None:
        """
        Stops the sensor without manual fan cleaning
        (auto-cleaning handles this weekly).
        """
        if not self.sensor:
            return

        try:
            self.sensor.stop_measurement()
            # No manual fan cleaning here — reduces fan life!
        except Exception as e:
            logging.error(f"Error stopping SPS30: {e}", exc_info=True)

    def read_data(self) -> dict:
        """
        Reads PM1.0, PM2.5, PM10 values.
        """
        data = {"pm1": None, "pm2_5": None, "pm10": None}

        if not self.working or not self.sensor:
            return data

        try:
            # Wait until data is available
            while not self.sensor.read_data_ready_flag():
                sleep(0.25)

            if self.sensor.read_measured_values() == self.sensor.MEASURED_VALUES_ERROR:
                raise RuntimeError("MEASURED VALUES CRC ERROR")

            data["pm1"] = round(self.sensor.dict_values.get("pm1p0", 0), 2)
            data["pm2_5"] = round(self.sensor.dict_values.get("pm2p5", 0), 2)
            data["pm10"] = round(self.sensor.dict_values.get("pm10p0", 0), 2)

        except Exception as e:
            logging.error(f"Error while reading SPS30 I2C data: {e}", exc_info=True)

        return data
