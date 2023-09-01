import smbus2
import bme280
import math
from time import sleep


class TPHSensor:
    """
    BME280 Temperature, Pressure and Humidity Sensor Class
    """

    def __init__(self, port=1, address=0x76):
        """
        Initialize the BME280 sensor.

        Args:
            port (int): The I2C bus port number (default is 1).
            address (int): The I2C address of the BME280 sensor (default is 0x76).
        """
        self.port = port
        self.address = address
        self.bus = smbus2.SMBus(self.port)
        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)

    
    def read_data(self):
        """
        Read temperature, pressure, humidity, and altitude from the BME280 sensor.

        Returns:
            dict: A dictionary containing the sensor data.
        """
        data = bme280.sample(self.bus, self.address, self.calibration_params)
        return {
            "temperature": round(data.temperature, 2),
            "pressure": round(data.pressure, 2),
            "humidity": round(data.humidity, 2)
        }

