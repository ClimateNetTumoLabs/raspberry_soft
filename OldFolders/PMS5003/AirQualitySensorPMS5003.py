"""
    Module for interacting with an air quality sensor (PMS5003).

    This module provides a class, AirQualitySensor, for reading air quality data from a PMS5003 air quality sensor.

    Class Docstring:
    ----------------
    AirQualitySensor:
        Interacts with a PMS5003 air quality sensor to read air quality data.

    Constructor:
        Initializes an AirQualitySensor object based on the configuration specified in the SENSORS module.

    Class Attributes:
        working (bool): Indicates if the air quality sensor is operational.
        pms5003 (PMS5003): An instance of the PMS5003 air quality sensor.

    Methods:
        read_data(self) -> dict:
            Attempts to read air quality data from the PMS5003 sensor, handling exceptions and returning the data as a dictionary.

    Module Usage:
    -------------
    To use this module, create an instance of the AirQualitySensor class. Call the read_data() method to get air quality data.
"""

from PMS5003_library import PMS5003


class AirQualitySensor:
    """
    Interacts with a PMS5003 air quality sensor to read air quality data.

    Attributes:
        working (bool): Indicates if the air quality sensor is operational.
        pms5003 (PMS5003): An instance of the PMS5003 air quality sensor.
    """

    def __init__(self) -> None:
        """
        Initializes an AirQualitySensor object based on the configuration specified in the SENSORS module.
        """

        self.working = True

        if self.working:
            self.pms5003 = PMS5003(
                device="/dev/ttyS0",
                baudrate=9600,
                pin_enable=22,
                pin_reset=27,
                pin_enable_working=True
            )

        # self.pms5003.stop()

    def __get_data(self) -> dict:
        """
        Retrieves air quality data from the PMS5003 sensor.

        Returns:
            dict: A dictionary containing various air quality measurements.
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
        Attempts to read air quality data from the PMS5003 sensor, handling exceptions and returning the data as a
        dictionary.

        Returns:
            dict: A dictionary containing air quality data. If an error occurs, returns a dictionary with None values.
        """
        if self.working:
            self.pms5003.setup()
            for i in range(3):
                try:
                    return self.__get_data()
                except Exception as e:
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


a = AirQualitySensor()

while True:
    print(a.read_data())
