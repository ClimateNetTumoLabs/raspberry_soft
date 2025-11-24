import time
from sps30 import SPS30 as SPS30I2C
from config import SENSORS
from logger_config import logging
from .SPS30_lib import SPS30 as SPS30UART


class SPS30Sensor:
    def __init__(self):
        self.sensor = None
        self.mode = None
        self.is_started = False  # Prevents calling start() multiple times and ensures sensor is ready before reading

        conf = SENSORS["sps30"]
        self.warmup_time = conf["warmup"]

        # Skip if both modes are disabled
        if not conf["i2c"]["working"] and not conf["uart"]["working"]:
            logging.info("[SPS30] Disabled in config")
            return

        # Case 2: Determine priority only when at least one is True
        if conf["i2c"]["working"] and not conf["uart"]["working"]:
            modes_priority = ["i2c", "uart"]
        elif conf["uart"]["working"] and not conf["i2c"]["working"]:
            modes_priority = ["uart", "i2c"]
        else:
            modes_priority = ["uart", "i2c"]

        # Try each mode in priority order until one works
        for mode in modes_priority:
            if mode == "i2c" and self.sensor is None:
                self.setup_i2c(conf["i2c"])
            elif mode == "uart" and self.sensor is None:
                self.setup_uart(conf["uart"])

        if not self.sensor:
            logging.error("[SPS30] Failed to initialize any mode")

    def setup_i2c(self, conf):
        """Initialize I2C connection"""
        try:
            sensor = SPS30I2C(conf["port"])

            if sensor.read_article_code() == sensor.ARTICLE_CODE_ERROR:
                raise RuntimeError("CRC ERROR on I2C")

            self.sensor = sensor
            self.mode = "i2c"
            logging.info("[SPS30] I2C initialized")
        except Exception as e:
            logging.error(f"[SPS30] I2C init failed: {e}")

    def setup_uart(self, conf):
        """Initialize UART connection"""
        try:
            self.sensor = SPS30UART(conf["address"], conf["baudrate"], conf["timeout"])
            self.sensor.resetDevice()
            self.mode = "uart"
            logging.info("[SPS30] UART initialized")
        except Exception as e:
            logging.error(f"[SPS30] UART init failed: {e}")

    def start(self):
        """Start measurement and warm up sensor"""
        if not self.sensor or self.is_started:
            return

        try:
            # Start measurement
            if self.mode == "i2c":
                self.sensor.start_measurement()
            else:  # uart
                self.sensor.startMeasurement()

            self.is_started = True

            # Warm up sensor
            logging.info(f"[SPS30] Warming up for {self.warmup_time}s...")
            start_time = time.time()
            while time.time() - start_time < self.warmup_time:
                time.sleep(0.5)

            logging.info("[SPS30] Ready")

        except Exception as e:
            logging.error(f"[SPS30] Start failed: {e}")
            self.is_started = False

    def read_data(self):
        """Read PM values from sensor"""
        data = {"pm1": None, "pm2_5": None, "pm10": None}

        if not self.sensor or not self.is_started:
            return data

        try:
            if self.mode == "i2c":
                # I2C mode
                if not self.sensor.read_data_ready_flag():
                    return data

                self.sensor.read_measured_values()
                vals = self.sensor.dict_values
                data["pm1"] = round(vals.get("pm1p0", 0), 2)
                data["pm2_5"] = round(vals.get("pm2p5", 0), 2)
                data["pm10"] = round(vals.get("pm10p0", 0), 2)

            else:  # uart
                vals = self.sensor.readMeasurement()
                if vals:
                    data["pm1"] = round(vals.get("Mass PM1.0", 0), 2)
                    data["pm2_5"] = round(vals.get("Mass PM2.5", 0), 2)
                    data["pm10"] = round(vals.get("Mass PM10", 0), 2)

        except Exception as e:
            logging.error(f"[SPS30] Read failed: {e}")

        return data

    def stop(self):
        """Stop measurement"""
        if not self.sensor or not self.is_started:
            return

        try:
            if self.mode == "i2c":
                self.sensor.stop_measurement()
            else:  # uart
                self.sensor.stopMeasurement()

            self.is_started = False
            logging.info("[SPS30] Stopped")

        except Exception as e:
            logging.error(f"[SPS30] Stop failed: {e}")