import adafruit_sht4x
import busio, board
from config import SENSORS
from logger_config import logging

class SHT45Sensor:
    def __init__(self):
        conf = SENSORS["sht45"]
        self.working = conf["working"]
        self.address = conf["address"]
        self.sensor = None

        if self.working:
            self.setup_sensor()
        else:
            logging.info("[SHT45] Disabled in config")

    def setup_sensor(self):
        try:
            self.sensor = adafruit_sht4x.SHT4x(busio.I2C(board.SCL, board.SDA), self.address)
            # Heater off: it warms the sensor and would skew temperature.
            self.sensor.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
            logging.info(f"[SHT45] Initialized, serial {self.sensor.serial_number:#x}")
        except Exception as e:
            logging.error(f"[SHT45] Init failed: {e}")
            self.sensor = None

    def read_data(self):
        # No pressure sensor on the SHT45, so pressure is sent as null.
        data = {"temperature": None, "pressure": None, "humidity": None}

        if self.working and self.sensor:
            try:
                temperature, humidity = self.sensor.measurements
            except (RuntimeError, OSError) as e:
                logging.error(f"[SHT45] Error while reading: {e}")
            except Exception as e:
                logging.error(f"[SHT45] Unhandled exception while reading: {e}", exc_info=True)
            else:
                data["temperature"] = round(temperature, 2)
                data["humidity"] = round(humidity, 2)

        return data

if __name__=="__main__":
    th = SHT45Sensor()
    print(th.read_data())
