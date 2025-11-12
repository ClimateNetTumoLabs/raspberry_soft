from adafruit_ltr390 import LTR390
from config import SENSORS
import busio, board

class LTR390Sensor:
    def __init__(self):
        conf = SENSORS["ltr390"]
        self.enabled = conf["working"]
        try:
            if self.enabled:
                i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = LTR390(i2c)
                print("[LTR390] Initialized")
            else:
                print("[LTR390] Disabled in config")
        except Exception as e:
            print(f"[LTR390] Initialization failed: {e}")
            self.connected = False

    def read_data(self):
        if not self.enabled:
            return {"uv": None, "lux": None}
        try:
            uv = self.sensor.uvi
            lux = self.sensor.lux
            return {"uv": round(uv), "lux": round(lux, 2)}
        except Exception as e:
            print(f"[LTR390] Read failed: {e}")
            return {"uv": None, "lux": None}

if __name__=="__main__":
    uv = LTR390Sensor()
    print(uv.read_data())