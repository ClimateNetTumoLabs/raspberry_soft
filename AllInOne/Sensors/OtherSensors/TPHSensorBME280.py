"""
    Module for interacting with a TPH (Temperature, Pressure, Humidity) sensor.

    This module provides a class, TPHSensor, for reading data from a specified TPH sensor.

    Class Docstring:
    ----------------
    TPHSensor:
        Interacts with a TPH sensor to read temperature, pressure, and humidity data.

    Constructor:
        Initializes a TPHSensor object based on the configuration specified in the SENSORS module.

    Class Attributes:
        working (bool): Indicates if the TPH sensor is operational.
        port (int): The port to which the sensor is connected.
        address (int): I2C address of the sensor.
        bus: (smbus2.SMBus): An instance of the SMBus for communication with the sensor.
        calibration_params: Calibration parameters for the sensor.

    Methods:
        read_data(self): Read temperature, pressure, and humidity data from the sensor, handling exceptions and returning the data.

    Module Usage:
    -------------
    To use this module, create an instance of the TPHSensor class. Call the read_data() method to get TPH data.
"""

import smbus2
import bme280
from logger_config import *
from config import SENSORS


class TPHSensor:
    """
    Interacts with a TPH sensor to read temperature, pressure, and humidity data.

    Attributes:
        working (bool): Indicates if the TPH sensor is operational.
        port (int): The port to which the sensor is connected.
        address (int): I2C address of the sensor.
        bus: (smbus2.SMBus): An instance of the SMBus for communication with the sensor.
        calibration_params: Calibration parameters for the sensor.
    """
    def __init__(self, port=1, address=0x76, testing=False):
        """
        Initializes a TPHSensor object based on the configuration specified in the SENSORS module.
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
        Read temperature, pressure, and humidity data from the sensor, handling exceptions and returning the data.

        Returns:
            dict: A dictionary containing temperature, pressure, and humidity data. If an error occurs, returns a dictionary with None values.
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
