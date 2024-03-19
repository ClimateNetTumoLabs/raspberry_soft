import smbus2
import bme280
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

        if self.working or self.testing:
            for i in range(3):
                try:
                    self.port = port
                    self.address = address
                    self.bus = smbus2.SMBus(self.port)
                    self.calibration_params = bme280.load_calibration_params(self.bus, self.address)
                    break
                except OSError:
                    logging.error("Error occurred during creating object for TPH sensor: [Errno 5] Input/output error")
                except Exception as e:
                    logging.error(f"Error occurred during creating object for TPH sensor: {str(e)}", exc_info=True)

                if i == 2:
                    self.working = False

    def read_data(self) -> dict:
        """
        Reads data from the TPH sensor and returns a dictionary of temperature, pressure, and humidity values.

        If the sensor is working or in testing mode, attempts to read TPH data.
        Logs any errors encountered during the reading process.

        Returns:
            dict: Dictionary containing temperature, pressure, and humidity values.
        """
        if self.working or self.testing:
            for i in range(3):
                try:
                    data = bme280.sample(self.bus, self.address, self.calibration_params)
                    return {
                        "temperature": round(data.temperature, 2),
                        "pressure": round(data.pressure * 0.750061, 2),
                        "humidity": round(data.humidity, 2)
                    }
                except Exception as e:
                    if isinstance(e, OSError):
                        logging.error(
                            f"Error occurred during reading data from TPH sensor: [Errno 121] Remote I/O error")
                    else:
                        logging.error(f"Error occurred during reading data from TPH sensor: {str(e)}", exc_info=True)
                    if i == 2:
                        return {
                            "temperature": None,
                            "pressure": None,
                            "humidity": None
                        }
        else:
            return {
                "temperature": None,
                "pressure": None,
                "humidity": None
            }
