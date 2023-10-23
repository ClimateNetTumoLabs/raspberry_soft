import smbus2
import bme280
from logger_config import *


class TPHSensor:
    """
    Class for reading temperature, pressure, and humidity data using a BME280 sensor.

    This class provides methods for reading temperature, pressure, and humidity data from a BME280 sensor
    connected to the Raspberry Pi using the I2C protocol.

    Args:
        port (int): The I2C port number (default is 1).
        address (int): The I2C address of the BME280 sensor (default is 0x76).

    Attributes:
        port (int): The I2C port number.
        address (int): The I2C address of the BME280 sensor.
        bus (SMBus2.SMBus): The I2C bus for communication.
        calibration_params: Calibration parameters for the BME280 sensor.

    Methods:
        read_data(self):
            Attempt to read temperature, pressure, and humidity data multiple times, handling exceptions
            and returning the data as a dictionary.
    """

    def __init__(self, port=1, address=0x76):
        """
        Initialize the TPHSensor class.

        This method initializes the TPHSensor class and sets up the I2C port, the address of the BME280 sensor,
        and loads calibration parameters.

        Args:
            port (int): The I2C port number (default is 1).
            address (int): The I2C address of the BME280 sensor (default is 0x76).

        Returns:
            None
        """
        self.port = port
        self.address = address
        self.bus = smbus2.SMBus(self.port)
        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)

    def read_data(self):
        """
        Attempt to read temperature, pressure, and humidity data multiple times, handling exceptions
        and returning the data as a dictionary.

        This method attempts to read temperature, pressure, and humidity data from the BME280 sensor multiple times,
        handling exceptions that may occur during the reading process. It returns the data as a dictionary with
        keys "temperature," "pressure," and "humidity."

        Returns:
            dict: A dictionary containing temperature, pressure, and humidity data.
        """
        for i in range(3):
            try:
                data = bme280.sample(self.bus, self.address, self.calibration_params)
                return {
                    "temperature": round(data.temperature, 2),
                    "pressure": round(data.pressure, 2),
                    "humidity": round(data.humidity, 2)
                }
            except Exception as e:
                if isinstance(e, OSError):
                    logging.error(f"Error occurred during reading data from TPH sensor: [Errno 121] Remote I/O error")
                else:
                    logging.error(f"Error occurred during reading data from TPH sensor: {str(e)}", exc_info=True)
                if i == 2:
                    return {
                        "temperature": None,
                        "pressure": None,
                        "humidity": None
                    }
