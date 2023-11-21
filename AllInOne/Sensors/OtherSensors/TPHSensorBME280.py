import smbus2
import bme280
from logger_config import *
from config import SENSORS

class TPHSensor:
    def __init__(self, port=1, address=0x76):
        sensor_info = SENSORS["tph_sensor"]

        self.working = sensor_info["working"]

        if self.working:
            self.port = port
            self.address = address
            self.bus = smbus2.SMBus(self.port)
            self.calibration_params = bme280.load_calibration_params(self.bus, self.address)

    def read_data(self):
        if self.working:
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
        else:
            return {
                "temperature": None,
                "pressure": None,
                "humidity": None
            }
