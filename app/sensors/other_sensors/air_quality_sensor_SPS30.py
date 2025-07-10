from config import SENSORS
from logger_config import logging
from serial.serialutil import SerialException
import time

# from .PMS5003_lib import PMS5003, SerialTimeoutError, ReadTimeoutError, ChecksumMismatchError
from  .SPS30_lib import SPS30

class AirQualitySensor:
    """
    Interface for interacting with the SPS30 air quality sensor.

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
        for i in range(3):
            try:
                self.sensor = SPS30(
                    port=self.sensor_info["port"],
                    baudrate=self.sensor_info["baudrate"],
                    timeout=self.sensor_info["timeout"],
                )
                break
            except Exception as e:
                logging.error(f"Error occurred during creating object for SPS30 sensor: {e}")

        if self.sensor:
            try:
                self.sensor.getVersion()
                self.sensor.startFanCleaning()
                return True
            except Exception as e:
                logging.error(f"Error occurred during setup SPS30 sensor: {e}")

            return False


    def stop(self) -> None:
        """
        Stops the SPS30 sensor.
        """
        try:
            self.sensor.stopMeasurement()
            self.sensor.stop()
        except Exception as e:
            logging.error(f"Error occurred during stopping SPS30 sensor: {e}")

    def read_data(self) -> dict:
        """
        Reads air quality data from the PMS5003 sensor.

        Returns:
            dict: Dictionary containing air quality data (pm1, pm2_5, pm10).
        """
        data = {"pm1": None, "pm2_5": None, "pm10": None}

        if self.working:
            if self.sensor is None:
                if not self.setup_sensor():
                    return data

            try:
                self.sensor.startMeasurement()
                time.sleep(5)
                sensor_data = self.sensor.readMeasurement()
                data["pm1"] = sensor_data['Mass PM1.0']
                data["pm2_5"] = sensor_data['Mass PM2.5']
                data["pm10"] = sensor_data['Mass PM10']
            except Exception as e:
                logging.error(f"Unhandled exception while reading PMS5003: {e}", exc_info=True)

        return data
