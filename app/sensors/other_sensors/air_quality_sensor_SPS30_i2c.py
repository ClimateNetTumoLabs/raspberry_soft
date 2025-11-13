from sps30 import SPS30
from time import sleep
from config import SENSORS
from logger_config import logging


class AirQualitySensor:
    """
    Interface for interacting with the SPS30 air quality sensor (I2C version).

    Attributes:
        sensor (SPS30 or None): Instance of the SPS30 sensor.
        sensor_info (dict): Configuration information for the sensor.
        working (bool): Indicates if the sensor is working.
    """

    def __init__(self) -> None:
        """
        Initializes the AirQualitySensor instance.
        """
        self.sensor = None
        self.sensor_info = SENSORS["air_quality_sensor"]
        self.working = self.sensor_info["working"]

        if self.working:
            self.setup_sensor()

    def setup_sensor(self) -> bool:
        """
        Sets up the SPS30 sensor instance.

        Returns:
            bool: True if sensor setup was successful, False otherwise.
        """
        try:
            # Initialize on I2C bus (default: 1)
            bus = self.sensor_info.get("bus", 1)
            self.sensor = SPS30(bus)

            # Verify sensor is responsive
            if self.sensor.read_article_code() == self.sensor.ARTICLE_CODE_ERROR:
                raise RuntimeError("ARTICLE CODE CRC ERROR")

            logging.info("SPS30 sensor initialized successfully.")
            return True
        except Exception as e:
            logging.error(f"Error occurred during SPS30 setup: {e}", exc_info=True)
            self.sensor = None
            return False

    def start(self) -> None:
        """
        Starts the SPS30 sensor measurement.
        """
        if not self.sensor:
            return

        try:
            self.sensor.start_measurement()
            sleep(30)  # warm-up time
        except Exception as e:
            logging.error(f"Error occurred during starting SPS30: {e}", exc_info=True)

    def stop(self) -> None:
        """
        Stops the SPS30 sensor.
        """
        if not self.sensor:
            return

        try:
            self.sensor.stop_measurement()
            self.sensor.start_fan_cleaning()
        except Exception as e:
            logging.error(f"Error occurred during stopping SPS30: {e}", exc_info=True)

    def read_data(self) -> dict:
        """
        Reads air quality data from the SPS30 sensor.

        Returns:
            dict: Dictionary containing air quality data (pm1, pm2_5, pm10).
        """
        data = {"pm1": None, "pm2_5": None, "pm10": None}

        if not self.working or self.sensor is None:
            return data

        try:
            # Wait until data is ready
            while not self.sensor.read_data_ready_flag():
                sleep(0.25)
                if self.sensor.read_data_ready_flag() == self.sensor.DATA_READY_FLAG_ERROR:
                    raise RuntimeError("DATA READY FLAG CRC ERROR")

            # Fetch measured values
            if self.sensor.read_measured_values() == self.sensor.MEASURED_VALUES_ERROR:
                raise RuntimeError("MEASURED VALUES CRC ERROR")

            data["pm1"] = round(self.sensor.dict_values.get("pm1p0", 0), 2)
            data["pm2_5"] = round(self.sensor.dict_values.get("pm2p5", 0), 2)
            data["pm10"] = round(self.sensor.dict_values.get("pm10p0", 0), 2)

        except Exception as e:
            logging.error(f"Unhandled exception while reading SPS30: {e}", exc_info=True)

        return data
