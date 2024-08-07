from config import SENSORS
from logger_config import logging
from serial.serialutil import SerialException

from .PMS5003_lib import PMS5003, SerialTimeoutError, ReadTimeoutError, ChecksumMismatchError


class AirQualitySensor:
    """
    Interface for interacting with the PMS5003 air quality sensor.

    Attributes:
        sensor (PMS5003 or None): Instance of the PMS5003 sensor.
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
            if self.sensor is not None:
                self.stop()

    def setup_sensor(self) -> bool:
        """
        Sets up the PMS5003 sensor instance.

        Returns:
            bool: True if sensor setup was successful, False otherwise.
        """
        for i in range(3):
            try:
                self.sensor = PMS5003(
                    device=self.sensor_info["address"],
                    baudrate=self.sensor_info["baudrate"],
                    pin_enable=self.sensor_info["pin_enable"],
                    pin_reset=self.sensor_info["pin_reset"]
                )
                break
            except Exception as e:
                logging.error(f"Error occurred during creating object for PMS5003 sensor: {e}")

        return self.sensor is not None

    def stop(self) -> None:
        """
        Stops the PMS5003 sensor.
        """
        try:
            self.sensor.stop()
        except Exception as e:
            logging.error(f"Error occurred during stopping PMS5003 sensor: {e}")

    def read_data(self) -> dict:
        """
        Reads air quality data from the PMS5003 sensor.

        Returns:
            dict: Dictionary containing air quality data (pm1, pm2_5, pm10).
        """
        data = {"pm1": None, "pm2_5": None, "pm10": None}

        if self.working:
            if self.sensor is None or self.sensor.get_pin_state() == "LOW":
                if not self.setup_sensor():
                    return data

            try:
                all_data = self.sensor.read()
                data["pm1"] = all_data.pm_ug_per_m3(size=1.0)
                data["pm2_5"] = all_data.pm_ug_per_m3(size=2.5)
                data["pm10"] = all_data.pm_ug_per_m3(size=10)
            except SerialTimeoutError as e:
                logging.error(f"SerialTimeout error while reading PMS5003: {e}")
            except ReadTimeoutError as e:
                logging.error(f"ReadTimeout error while reading PMS5003: {e}")
            except SerialException as e:
                logging.error(f"SerialException error while reading PMS5003: {e}")
            except ChecksumMismatchError as e:
                logging.error(f"ChecksumMismatch error while reading PMS5003: {e}")
            except Exception as e:
                logging.error(f"Unhandled exception while reading PMS5003: {e}", exc_info=True)

        return data
