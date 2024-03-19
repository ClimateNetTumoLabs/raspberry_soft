from .PMS5003_library import PMS5003, SerialTimeoutError, ReadTimeoutError
from logger_config import *
from config import SENSORS


class AirQualitySensor:
    """
    Represents an air quality sensor for measuring particulate matter (PM) concentration.

    This class interacts with a PMS5003 air quality sensor module to measure various aspects of particulate matter
    concentration in the air, including PM1, PM2.5, and PM10.

    Args:
        testing (bool, optional): Specifies whether the sensor is in testing mode. Defaults to False.

    Attributes:
        working (bool): Indicates if the sensor is functioning properly.
        testing (bool): Specifies whether the sensor is in testing mode.
        pms5003 (PMS5003): Instance of the PMS5003 air quality sensor module.

    Methods:
        read_data() -> dict: Reads data from the sensor and returns a dictionary of air quality values.

    """

    def __init__(self, testing=False) -> None:
        """
        Initializes the AirQualitySensor object.

        If the sensor is working or in testing mode, attempts to create an object for the air quality sensor module.
        Logs any errors encountered during the initialization process.

        Args:
            testing (bool, optional): Specifies whether the sensor is in testing mode. Defaults to False.
        """
        sensor_info = SENSORS["air_quality_sensor"]

        self.working = sensor_info["working"]
        self.testing = testing

        if self.working or self.testing:
            for i in range(3):
                try:
                    self.pms5003 = PMS5003(
                        device=sensor_info["address"],
                        baudrate=sensor_info["baudrate"],
                        pin_enable=sensor_info["pin_enable"],
                        pin_reset=sensor_info["pin_reset"]
                    )
                    break
                except Exception as e:
                    if i == 2:
                        self.working = False
                    logging.error(f"Error occurred during creating object for AirQuality sensor: {str(e)}", exc_info=True)

    def __get_data(self) -> dict:
        """
        Reads raw data from the air quality sensor and calculates various air quality values.

        Returns:
            dict: Dictionary containing air quality values.
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

    def read_data(self) -> dict:
        """
        Reads data from the air quality sensor and returns a dictionary of air quality values.

        If the sensor is working or in testing mode, attempts to read air quality data.
        Logs any errors encountered during the reading process.

        Returns:
            dict: Dictionary containing air quality values.
        """
        if self.working or self.testing:
            for i in range(3):
                try:
                    return self.__get_data()
                except Exception as e:
                    if isinstance(e, SerialTimeoutError):
                        logging.error(f"Error occurred during reading data from AirQuality sensor: PMS5003 "
                                      f"SerialTimeoutError: Failed to read start of frame byte")
                    elif isinstance(e, ReadTimeoutError):
                        logging.error(f"Error occurred during reading data from AirQuality sensor: PMS5003 "
                                      f"ReadTimeoutError: Could not find start of frame")
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
