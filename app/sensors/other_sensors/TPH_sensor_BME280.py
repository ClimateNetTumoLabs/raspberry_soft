import bme280
import smbus2
from config import SENSORS
from logger_config import logging


class TPHSensor:
    """
    Class for interacting with the BME280 Temperature, Pressure, and Humidity Sensor.

    Attributes:
        bus (smbus2.SMBus or None): SMBus object for I2C communication.
        calibration_params (bme280.CalibrationParams or None): Calibration parameters for sensor.
        sensor (bool or None): Indicates if sensor setup was successful.
        sensor_info (dict): Configuration information for the sensor.
        working (bool): Indicates if the sensor is operational.
        port (int): Port number for the sensor's I2C communication.

    Methods:
        setup_sensor: Initializes the sensor setup.
        read_data: Reads temperature, pressure, and humidity data from the sensor.
    """

    def __init__(self):
        """
        Initializes the TPHSensor instance.
        """
        self.bus = None
        self.calibration_params = None
        self.sensor = None
        self.sensor_info = SENSORS["tph_sensor"]
        self.working = self.sensor_info["working"]
        self.port = self.sensor_info["port"]

        if self.working:
            self.setup_sensor()

    def setup_sensor(self) -> bool:
        """
        Sets up the sensor by initializing the SMBus and loading calibration parameters.

        Returns:
            bool: True if sensor setup was successful, False otherwise.
        """
        for i in range(3):
            try:
                self.bus = smbus2.SMBus(self.port)
                self.calibration_params = bme280.load_calibration_params(self.bus)
                self.sensor = True
                break
            except Exception as e:
                logging.error(f"Error occurred during creating object for BME280 sensor: {e}")

        return self.sensor is not None

    def read_data(self) -> dict:
        """
        Reads temperature, pressure, and humidity data from the sensor.

        Returns:
            dict: Dictionary containing temperature, pressure, and humidity data.
        """
        data = {"temperature": None, "pressure": None, "humidity": None}

        if self.working:
            if not self.sensor:
                if not self.setup_sensor():
                    return data
            try:
                result = bme280.sample(bus=self.bus, compensation_params=self.calibration_params)
            except AttributeError as e:
                logging.error(f"Attribute error while reading BME280: {e}")
            except OSError as e:
                logging.error(f"OS error while reading BME280: {e}")
            except Exception as e:
                logging.error(f"Unhandled exception while reading BME280: {e}", exc_info=True)
            else:
                data["temperature"] = round(result.temperature, 2)
                data["pressure"] = round(result.pressure * 0.750061, 2)
                data["humidity"] = round(result.humidity, 2)

        return data
