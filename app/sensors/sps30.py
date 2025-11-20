import time
from sps30 import SPS30 as SPS30I2C
from config import SENSORS
from logger_config import logging
from .SPS30_lib import SPS30 as SPS30UART


class SPS30Sensor:
    def __init__(self):
        self.sensor = None
        self.mode = None
        self.is_measuring = False  # Track if sensor is currently measuring

        conf = SENSORS["sps30"]
        self.warmup_time = conf["warmup"]

        # Case 1: BOTH False → skip sensor completely
        if not conf["i2c"]["working"] and not conf["uart"]["working"]:
            logging.info("[SPS30] Disabled in config → skipping sensor initialization")
            return

        # Case 2: Determine priority only when at least one is True
        if conf["i2c"]["working"] and not conf["uart"]["working"]:
            modes_priority = ["i2c", "uart"]
        elif conf["uart"]["working"] and not conf["i2c"]["working"]:
            modes_priority = ["uart", "i2c"]
        else:
            modes_priority = ["i2c", "uart"]

        # Initialize hardware connection but don't start measurement yet
        for mode in modes_priority:
            if mode == "i2c" and self.sensor is None:
                self.setup_i2c(conf["i2c"])
            elif mode == "uart" and self.sensor is None:
                self.setup_uart(conf["uart"])

        if not self.sensor:
            logging.error("[SPS30] No working mode found (I2C or UART)")

    def setup_i2c(self, conf):
        try:
            sensor = SPS30I2C(conf["port"])

            if sensor.read_article_code() == sensor.ARTICLE_CODE_ERROR:
                raise RuntimeError("CRC ERROR on I2C")

            self.sensor = sensor
            self.mode = "i2c"
            logging.info("[SPS30] I2C mode initialized (not started)")

        except Exception as e:
            logging.error(f"[SPS30] I2C init failed: {e}")

    def setup_uart(self, conf):
        try:
            address = conf["address"]
            baudrate = conf["baudrate"]
            timeout = conf["timeout"]
            sensor = SPS30UART(address, baudrate, timeout)
            sensor.resetDevice()

            test = sensor.readDeviceInfo()

            if not test:
                raise RuntimeError("UART no response")

            self.sensor = sensor
            self.mode = "uart"
            logging.info("[SPS30] UART mode initialized (not started)")

        except Exception as e:
            logging.error(f"[SPS30] UART init failed: {e}")

    def enable_auto_cleaning(self):
        """Enable fan auto-cleaning every 7 days (both modes). Only set once."""
        if not self.sensor:
            return

        try:
            if self.mode == "i2c":
                self.sensor.set_auto_cleaning_interval(604800)
            elif self.mode == "uart":
                self.sensor.setAutoCleaningInterval(604800)

            logging.info("[SPS30] Auto-cleaning interval set to 7 days")
        except Exception as e:
            logging.error(f"[SPS30] Failed to set auto-cleaning: {e}")

    def start(self):
        """Start measurement and warm up - called once at beginning of measurement period"""
        if not self.sensor or self.is_measuring:
            return

        try:
            # Set auto-cleaning before starting (only happens once)
            self.enable_auto_cleaning()

            if self.mode == "i2c":
                self.sensor.start_measurement()
            elif self.mode == "uart":
                self.sensor.startMeasurement()

            self.is_measuring = True
            logging.info(f"[SPS30] Starting measurement, warming up for {self.warmup_time}s...")
            time.sleep(self.warmup_time)
            logging.info("[SPS30] Warmup complete, ready for readings")

        except Exception as e:
            logging.error(f"[SPS30] Error during start: {e}", exc_info=True)
            self.is_measuring = False

    def read_data(self):
        """Read data from sensor - assumes sensor is already started"""
        data = {"pm1": None, "pm2_5": None, "pm10": None}

        if not self.sensor or not self.is_measuring:
            return data

        try:
            if self.mode == "i2c":
                if not self.sensor.read_data_ready_flag():
                    return data

                if self.sensor.read_measured_values() == self.sensor.MEASURED_VALUES_ERROR:
                    raise RuntimeError("I2C MEASUREMENT CRC ERROR")

                vals = self.sensor.dict_values
                data["pm1"] = round(vals.get("pm1p0", 0), 2)
                data["pm2_5"] = round(vals.get("pm2p5", 0), 2)
                data["pm10"] = round(vals.get("pm10p0", 0), 2)

            elif self.mode == "uart":
                values = self.sensor.readMeasurement()
                if not values:
                    return data

                data["pm1"] = round(values.get("Mass PM1.0", 0), 2)
                data["pm2_5"] = round(values.get("Mass PM2.5", 0), 2)
                data["pm10"] = round(values.get("Mass PM10", 0), 2)

        except OSError as e:
            if e.errno == 121:
                logging.warning(f"[SPS30] I2C communication error")
            else:
                logging.error(f"[SPS30] OS error reading data: {e}")
        except Exception as e:
            logging.error(f"[SPS30] Failed to read data ({self.mode}): {e}")

        return data

    def stop(self):
        """Stop measurement - called after measurement period ends"""
        if not self.sensor or not self.is_measuring:
            return

        try:
            if self.mode == "i2c":
                self.sensor.stop_measurement()
            elif self.mode == "uart":
                self.sensor.stopMeasurement()

            self.is_measuring = False
            logging.info("[SPS30] Measurement stopped")
        except Exception as e:
            logging.error(f"[SPS30] Couldn't stop SPS30 ({self.mode}): {e}")