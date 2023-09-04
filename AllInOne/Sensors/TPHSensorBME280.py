import smbus2
import bme280
import logging
from time import sleep


logging.basicConfig(filename='parsing.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TPHSensor:
    def __init__(self, port=1, address=0x76):
        self.port = port
        self.address = address
        self.bus = smbus2.SMBus(self.port)
        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)

    
    def read_data(self):
        for i in range(3):
            try:
                data = bme280.sample(self.bus, self.address, self.calibration_params)
                return {
                    "temperature": round(data.temperature, 2),
                    "pressure": round(data.pressure, 2),
                    "humidity": round(data.humidity, 2)
                }
            except Exception as e:
                logging.error(f"Error occurred during reading data from TPH sensor: {str(e)}", exc_info=True)
                if i == 2:
                    return {
                        "temperature": None,
                        "pressure": None,
                        "humidity": None
                    }
            

