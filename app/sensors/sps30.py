import time
from sps30 import SPS30
from config import SENSORS

class SPS30Sensor:
    """SPS30 air quality sensor — simple, safe, and robust."""

    def __init__(self):
        conf = SENSORS["sps30_i2c"]
        self.enabled = conf["working"]
        try:
            if self.enabled:
                self.pm1 = None
                self.pm2_5 = None
                self.pm10 = None
                self.port = conf["port"]
                self.warmup_time = conf["warmup"]
                print("[SPS30] Initialized successfully")
            else:
                print("[SPS30] Skipped (disabled in config)")
        except Exception as e:
            print(f"[SPS30] Initialization failed: {e}")
            self.enabled = False

        try:
            self.sps = SPS30(self.port)
            if self.sps.read_article_code() == self.sps.ARTICLE_CODE_ERROR:
                raise RuntimeError("ARTICLE CODE CRC ERROR")

            self.sps.start_measurement()
            print(f"[SPS30] Initialized — warming up for {self.warmup_time}s")

            # Warm-up using non-blocking time tracking
            start = time.time()
            while time.time() - start < self.warmup_time:
                time.sleep(0.25)

        except Exception as e:
            print(f"[SPS30] Initialization failed: {e}")
            self.sps = None

    def read_data(self):
        """Take one SPS30 reading safely; returns dict with PM values or None."""
        if not self.sps:
            return {"pm1": None, "pm2_5": None, "pm10": None}

        try:
            ready_flag = self.sps.read_data_ready_flag()
            if ready_flag == self.sps.DATA_READY_FLAG_ERROR:
                raise RuntimeError("DATA READY FLAG CRC ERROR")

            if not ready_flag:
                return {"pm1": self.pm1, "pm2_5": self.pm2_5, "pm10": self.pm10}

            if self.sps.read_measured_values() == self.sps.MEASURED_VALUES_ERROR:
                raise RuntimeError("MEASURED VALUES CRC ERROR")

            vals = self.sps.dict_values
            self.pm1 = round(vals.get("pm1p0"), 2)
            self.pm2_5 = round(vals.get("pm2p5"), 2)
            self.pm10 = round(vals.get("pm10p0"), 2)

            return {"pm1": self.pm1, "pm2_5": self.pm2_5, "pm10": self.pm10}

        except Exception as e:
            print(f"[SPS30] Read failed: {e}")
            return {"pm1": None, "pm2_5": None, "pm10": None}

    def stop(self):
        """Safely stop measurement."""
        try:
            if self.sps:
                self.sps.stop_measurement()
        except Exception as e:
            print(f"[SPS30] Stop failed: {e}")


if __name__=="__main__":
    sps = SPS30Sensor()
    print(sps.read_data())
    sps.stop()