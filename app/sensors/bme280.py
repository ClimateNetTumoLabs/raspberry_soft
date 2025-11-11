import bme280
from smbus2 import SMBus
from config import SENSORS

class BME280Sensor:
    def __init__(self):
        conf = SENSORS["bme280"]
        self.enabled = conf["working"]
        self.calibration_loaded = False
        try:
            if self.enabled:
                self.bus = SMBus(conf["port"])
                self.address = conf["address"]
                self.calibration = bme280.load_calibration_params(self.bus, self.address)
                self.calibration_loaded = True
                print("[BME280] Initialized successfully")
            else:
                print("[BME280] Disabled in config")
        except Exception as e:
            print(f"[BME280] Initialization failed: {e}")
            self.enabled = False

    def read_data(self):
        if not self.enabled or not self.calibration_loaded:
            return {"temperature": None, "pressure": None, "humidity": None}
        try:
            data = bme280.sample(self.bus, self.address, self.calibration)
            return {
                "temperature": round(data.temperature, 2),
                "pressure": round(data.pressure, 2),
                "humidity": round(data.humidity, 2)
            }
        except Exception as e:
            print(f"[BME280] Read failed: {e}")
            return {"temperature": None, "pressure": None, "humidity": None}

if __name__=="__main__":
    tph = BME280Sensor()
    print(tph.read_data())