from .PMS5003_library import PMS5003
from logger_config import *


class AirQualitySensor:
    def __init__(self, device='/dev/ttyS0', baudrate=9600, pin_enable=27, pin_reset=22):
        self.device = device
        self.baudrate = baudrate
        self.pin_enable = pin_enable
        self.pin_reset = pin_reset
        self.pms5003 = PMS5003(device=device, baudrate=baudrate, pin_enable=pin_enable, pin_reset=pin_reset)

    def get_data(self):
        data = {}
        all_data = self.pms5003.read()

        data["Air_PM1"] = all_data.pm_ug_per_m3(1.0)
        data["Air_PM2_5"] = all_data.pm_ug_per_m3(2.5)
        data["Air_PM10"] = all_data.pm_ug_per_m3(10)

        return data

    def read_data(self):
        for i in range(3):
            try:
                return self.get_data()
            except Exception as e:
                logging.error(f"Error occurred during reading data from AirQuality sensor: {str(e)}", exc_info=True)
                if i == 2:
                    return {
                        "Air_PM1": None,
                        "Air_PM2_5": None,
                        "Air_PM10": None
                    }
