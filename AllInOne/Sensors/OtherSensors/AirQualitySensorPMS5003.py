from .PMS5003_library import PMS5003, SerialTimeoutError, ReadTimeoutError
from logger_config import *
from config import SENSORS


class AirQualitySensor:
    """
    Class for reading air quality data using a PMS5003 air quality sensor.

    This class provides methods for reading air quality data from a PMS5003 air quality sensor connected to
    a serial device, typically a Raspberry Pi's UART.

    Args:
        device (str): The path to the serial device (default is '/dev/ttyS0').
        baudrate (int): The baud rate for serial communication (default is 9600).
        pin_enable (int): GPIO pin number for enabling the sensor (default is 27).
        pin_reset (int): GPIO pin number for resetting the sensor (default is 22).

    Attributes:
        device (str): The path to the serial device.
        baudrate (int): The baud rate for serial communication.
        pin_enable (int): GPIO pin number for enabling the sensor.
        pin_reset (int): GPIO pin number for resetting the sensor.
        pms5003 (PMS5003): An instance of the PMS5003 air quality sensor.

    Methods:
        get_data(self):
            Read air quality data from the PMS5003 sensor and return a dictionary of particle concentration values.

        read_data(self):
            Attempt to read air quality data multiple times, handling exceptions and returning the data as a dictionary.
    """

    def __init__(self):
        """
        Initialize the AirQualitySensor class.

        This method initializes the AirQualitySensor class and sets up the serial device and GPIO pins.
        It also creates an instance of the PMS5003 air quality sensor.

        Args:
            device (str): The path to the serial device (default is '/dev/ttyS0').
            baudrate (int): The baud rate for serial communication (default is 9600).
            pin_enable (int): GPIO pin number for enabling the sensor (default is 27).
            pin_reset (int): GPIO pin number for resetting the sensor (default is 22).

        Returns:
            None
        """
        sensor_info = SENSORS["air_quality_sensor"]

        self.working = sensor_info["working"]

        if self.working:
            self.pms5003 = PMS5003(
                device=sensor_info["address"],
                baudrate=sensor_info["baudrate"],
                pin_enable=sensor_info["pin_enable"],
                pin_reset=sensor_info["pin_reset"]
            )

    def __get_data(self):
        """
        Read air quality data from the PMS5003 sensor and return a dictionary of particle concentration values.

        This method reads air quality data from the PMS5003 sensor, including particle concentration values
        for different particle sizes (PM1.0, PM2.5, and PM10).

        Returns:
            dict: A dictionary containing air quality data with keys "Air_PM1", "Air_PM2_5", and "Air_PM10."
        """
        data = {}
        all_data = self.pms5003.read()

        data["pm1"] = all_data.pm_ug_per_m3(size=1.0)
        data["pm2_5"] = all_data.pm_ug_per_m3(size=2.5)
        data["pm10"] = all_data.pm_ug_per_m3(size=10)

        data["atm_pm1"] = all_data.pm_ug_per_m3(size=1.0, atmospheric_environment=True)
        data["atm_pm2_5"] = all_data.pm_ug_per_m3(size=2.5, atmospheric_environment=True)
        data["atm_pm10"] = all_data.pm_ug_per_m3(size=10, atmospheric_environment=True)

        data["litre_pm0_3"] = all_data.pm_per_1l_air(size=0.3)
        data["litre_pm0_5"] = all_data.pm_per_1l_air(size=0.5)
        data["litre_pm1"] = all_data.pm_per_1l_air(size=1.0)
        data["litre_pm2_5"] = all_data.pm_per_1l_air(size=2.5)
        data["litre_pm5"] = all_data.pm_per_1l_air(size=5)
        data["litre_pm10"] = all_data.pm_per_1l_air(size=10)

        return data

    def read_data(self):
        """
        Attempt to read air quality data multiple times, handling exceptions, and returning the data as a dictionary.

        This method attempts to read air quality data from the PMS5003 sensor multiple times, handling exceptions
        that may occur during the reading process. It returns the data as a dictionary with particle concentration values.

        Returns:
            dict: A dictionary containing air quality data with keys "Air_PM1", "Air_PM2_5", and "Air_PM10."
        """
        if self.working:
            for i in range(3):
                try:
                    return self.__get_data()
                except Exception as e:
                    if isinstance(e, SerialTimeoutError):
                        logging.error(f"Error occurred during reading data from AirQuality sensor: PMS5003 SerialTimeoutError: Failed to read start of frame byte")
                    elif isinstance(e, ReadTimeoutError):
                        logging.error(f"Error occurred during reading data from AirQuality sensor: PMS5003 ReadTimeoutError: Could not find start of frame")
                    else:
                        logging.error(f"Error occurred during reading data from AirQuality sensor: {str(e)}", exc_info=True)
                    if i == 2:
                        return {
                            "pm1": None,
                            "pm2_5": None,
                            "pm10": None,
                            "atm_pm1": None,
                            "atm_pm2_5": None,
                            "atm_pm10": None,
                            "litre_pm0_3": None,
                            "litre_pm0_5": None,
                            "litre_pm1": None,
                            "litre_pm2_5": None,
                            "litre_pm5": None,
                            "litre_pm10": None
                        }

        else:
            return {
                "pm1": None,
                "pm2_5": None,
                "pm10": None,
                "atm_pm1": None,
                "atm_pm2_5": None,
                "atm_pm10": None,
                "litre_pm0_3": None,
                "litre_pm0_5": None,
                "litre_pm1": None,
                "litre_pm2_5": None,
                "litre_pm5": None,
                "litre_pm10": None
            }
