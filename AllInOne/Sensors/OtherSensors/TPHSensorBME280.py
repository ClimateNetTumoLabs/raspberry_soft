import time
import smbus2
import bme280
from Scripts.kalman_data_collector import KalmanDataCollector
from logger_config import *
from config import SENSORS


class TPHSensor:
    """
    Represents a temperature, pressure, and humidity (TPH) sensor for environmental monitoring.

    This class interacts with a BME280 sensor module to measure temperature, pressure, and humidity in the environment.

    Args:
        port (int, optional): The port number to which the sensor is connected. Defaults to 1.
        address (int, optional): The I2C address of the sensor. Defaults to 0x76.
        testing (bool, optional): Specifies whether the sensor is in testing mode. Defaults to False.

    Attributes:
        testing (bool): Specifies whether the sensor is in testing mode.
        working (bool): Indicates if the sensor is functioning properly.
        port (int): The port number to which the sensor is connected.
        address (int): The I2C address of the sensor.
        bus (smbus2.SMBus): Instance of the SMBus interface for communication with the sensor module.
        calibration_params (bme280.CalibrationParams): Calibration parameters for the BME280 sensor.

    Methods:
        read_data() -> dict: Reads data from the sensor and returns a dictionary of temperature, pressure, and humidity values.

    """

    def __init__(self, port=1, address=0x76, testing=False):
        """
        Initializes the TPHSensor object.

        If the sensor is working or in testing mode, attempts to create an object for the TPH sensor module.
        Logs any errors encountered during the initialization process.

        Args:
            port (int, optional): The port number to which the sensor is connected. Defaults to 1.
            address (int, optional): The I2C address of the sensor. Defaults to 0x76.
            testing (bool, optional): Specifies whether the sensor is in testing mode. Defaults to False.
        """
        sensor_info = SENSORS["tph_sensor"]
        self.testing = testing
        self.working = sensor_info["working"]
        self.reading_time = sensor_info['reading_time']

        if self.working or self.testing:
            for i in range(3):
                try:
                    self.port = port
                    self.address = address
                    self.bus = smbus2.SMBus(self.port)
                    self.calibration_params = bme280.load_calibration_params(self.bus, self.address)
                    break
                except OSError:
                    logging.error("Error occurred during creating object for BME280 sensor: [Errno 5] Input/output "
                                  "error")
                except Exception as e:
                    logging.error(f"Error occurred during creating object for BME280 sensor: {str(e)}", exc_info=True)

                if i == 2:
                    self.working = False

    def __get_data(self):
        data = bme280.sample(self.bus, self.address, self.calibration_params)

        return {
            "temperature": round(data.temperature, 2),
            "pressure": round(data.pressure * 0.750061, 2),
            "humidity": round(data.humidity, 2)
        }

    def read_data(self) -> dict:
        """
        Reads data from the TPH sensor and returns a dictionary of temperature, pressure, and humidity values.

        If the sensor is working or in testing mode, attempts to read TPH data.
        Logs any errors encountered during the reading process.

        Returns:
            dict: Dictionary containing temperature, pressure, and humidity values.
        """
        if self.testing:
            return self.__get_data()

        if self.working:
            kalman_data_collector = KalmanDataCollector('temperature', 'pressure', 'humidity')

            start_time = time.time()
            errors = []

            while time.time() - start_time <= self.reading_time:
                try:
                    data = self.__get_data()
                    kalman_data_collector.add_data(data)

                    time.sleep(3)
                except Exception as e:
                    errors.append(e)

            if not kalman_data_collector.is_valid():
                for error in errors:
                    logging.error(f"Error occurred during reading data from BME280 sensor: {str(error)}",
                                  exc_info=True)

                errors.clear()

                return {
                    "temperature": None,
                    "pressure": None,
                    "humidity": None
                }

            return kalman_data_collector.get_result()
        else:
            return {
                "temperature": None,
                "pressure": None,
                "humidity": None
            }
