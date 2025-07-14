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
                self.sensor.resetDevice()
                break
            except Exception as e:
                logging.error(f"Error occurred during creating object for SPS30 sensor: {e}")

        if self.sensor:
            try:
                version = self.sensor.getVersion()
                logging.info(version)
                print(version)
                return True
            except Exception as e:
                logging.error(f"Error occurred during setup SPS30 sensor: {e}")

            return False

    def start(self) -> None:
        try:
            statusRegister = self.sensor.readStatusRegister()
            speed_bit = statusRegister.get("Speed")
            laser_bit = statusRegister.get("Laser")
            fan_bit = statusRegister.get("Fan")

            if any(bit == 1 for bit in [speed_bit, laser_bit, fan_bit]):
                raise Exception("Invalid status register of SPS30")
            self.sensor.startMeasurement()
            time.sleep(1)
            self.sensor.startFanCleaning()
            time.sleep(5)
        except Exception as e:
            logging.error(f"Error occurred during starting SPS30 sensor: {e}")

    def stop(self) -> None:
        """
        Stops the SPS30 sensor.
        """
        if self.sensor:
            try:
                self.sensor.stopMeasurement()
            except Exception as e:
                logging.error(f"Error occurred during stopping SPS30 sensor: {e}")

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
            readings = self.sensor.readMeasurement()
            data["pm1"] = round(readings.get("Mass PM1.0", 0), 2)
            data["pm2_5"] = round(readings.get("Mass PM2.5", 0), 2)
            data["pm10"] = round(readings.get("Mass PM10", 0), 2)
        except Exception as e:
            logging.error(f"Unhandled exception while reading SPS30: {e}", exc_info=True)

        return data
