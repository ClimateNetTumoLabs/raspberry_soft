import logging
from Sensors.PMS5003_library import PMS5003


logging.basicConfig(filename='parsing.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class AirQualitySensor:
    def __init__(self, device='/dev/ttyS0', baudrate=9600, pin_enable=27, pin_reset=22):
        self.device = device
        self.baudrate = baudrate
        self.pin_enable = pin_enable
        self.pin_reset = pin_reset
        self.pms5003 = PMS5003(device=device, baudrate=baudrate, pin_enable=pin_enable, pin_reset=pin_reset)

    def read_data(self):
        for i in range(3):
            try:
                data = {}
                all_data = self.pms5003.read()

                data["PM1"] = all_data.pm_ug_per_m3(1.0)
                data["PM2_5"] = all_data.pm_ug_per_m3(2.5)
                data["PM10"] = all_data.pm_ug_per_m3(10)
                data["Atmospheric_PM1"] = all_data.pm_ug_per_m3(1.0, True)
                data["Atmospheric_PM2_5"] = all_data.pm_ug_per_m3(2.5, True)
                data["Atmospheric_PM10"] = all_data.pm_ug_per_m3(10, True)

                data["0_3um"] = all_data.pm_per_1l_air(0.3)
                data["0_5um"] = all_data.pm_per_1l_air(0.5)
                data["1_0um"] = all_data.pm_per_1l_air(1.0)
                data["2_5um"] = all_data.pm_per_1l_air(2.5)
                data["5um"] = all_data.pm_per_1l_air(5)
                data["10um"] = all_data.pm_per_1l_air(10)

                return data
            except Exception as e:
                logging.error(f"Error occurred during reading data from AirQuality sensor: {str(e)}", exc_info=True)
                if i == 2:
                    return {
                        "PM1": None,
                        "PM2_5": None,
                        "PM10": None,
                        "Atmospheric_PM1": None,
                        "Atmospheric_PM2_5": None,
                        "Atmospheric_PM10": None,
                        "0_3um": None,
                        "0_5um": None,
                        "1_0um": None,
                        "2_5um": None,
                        "5um": None,
                        "10um": None
                    }
