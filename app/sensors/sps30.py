import time
from .libs.SPS30_I2C import SPS30 as SPS30I2C
from config import SENSORS
from logger_config import logging
from .libs.SPS30_UART import SPS30 as SPS30UART


class SPS30Sensor:
    def __init__(self):
        self.sensor = None
        self.mode = None
        self.is_started = False

        conf = SENSORS["sps30"]
        self.warmup_time = conf["warmup"]

        # Skip if both modes are disabled
        if not conf["i2c"]["working"] and not conf["uart"]["working"]:
            logging.info("[SPS30] Disabled in config")
            return

        # Determine priority based on config
        if conf["i2c"]["working"] and not conf["uart"]["working"]:
            modes_priority = ["i2c", "uart"]
        elif conf["uart"]["working"] and not conf["i2c"]["working"]:
            modes_priority = ["uart", "i2c"]
        else:
            modes_priority = ["uart", "i2c"]  # Default: UART first

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

            # Test communication
            article_code = sensor.read_article_code()
            if article_code == sensor.ARTICLE_CODE_ERROR:
                raise RuntimeError("CRC ERROR on I2C")

            self.sensor = sensor
            self.mode = "i2c"

            # Set auto-cleaning interval (non-critical, don't fail if it errors)
            try:
                self.sensor.set_auto_cleaning_interval(604800)  # 7 days
                logging.info("[SPS30] Auto-cleaning set to 7 days")
            except Exception as e:
                logging.warning(f"[SPS30] Could not set auto-cleaning: {e}")

            logging.info(f"[SPS30] I2C initialized")

        except Exception as e:
            logging.error(f"[SPS30] I2C init failed: {e}")
            self.sensor = None

    def setup_uart(self, conf):
        """Initialize UART connection"""
        try:
            sensor = SPS30UART(conf["address"], conf["baudrate"], conf["timeout"])

            # Test communication
            sensor.resetDevice()
            device_info = sensor.readDeviceInfo()
            if not device_info:
                raise RuntimeError("No response from UART device")

            self.sensor = sensor
            self.mode = "uart"

            # Set auto-cleaning interval
            try:
                sensor.setAutoCleaningInterval(604800)  # 7 days
                logging.info("[SPS30] Auto-cleaning set to 7 days")
            except Exception as e:
                logging.warning(f"[SPS30] Could not set auto-cleaning: {e}")

            logging.info(f"[SPS30] UART initialized")

        except Exception as e:
            logging.error(f"[SPS30] UART init failed: {e}")
            self.sensor = None

    def start(self):
        """
        Start measurement and warm up sensor.
        Only starts if not already started.
        """
        if not self.sensor or self.is_started:
            if self.is_started:
                logging.debug("[SPS30] Already started, skipping")
            return

        try:
            if self.mode == "i2c":
                self.sensor.start_measurement()
            else:
                self.sensor.startMeasurement()

            self.is_started = True

            logging.info(f"[SPS30] Warming up for {self.warmup_time}s...")
            start_time = time.time()
            while time.time() - start_time < self.warmup_time:
                time.sleep(0.5)

            logging.info("[SPS30] Ready for readings")

        except Exception as e:
            logging.error(f"[SPS30] Start failed: {e}")
            self.is_started = False

    def read_data(self):
        """
        Read PM values from sensor.
        Returns dict with pm1, pm2_5, pm10 values.
        """
        data = {"pm1": None, "pm2_5": None, "pm10": None}

        if not self.sensor or not self.is_started:
            return data

        try:
            if self.mode == "i2c":
                # Check if data is ready
                if not self.sensor.read_data_ready_flag():
                    return data

                # Read measured values
                result = self.sensor.read_measured_values()
                if result == self.sensor.MEASURED_VALUES_ERROR:
                    logging.warning("[SPS30] Measurement CRC error")
                    return data

                # Extract values
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

        except OSError as e:
            if e.errno == 121:  # Remote I/O error
                logging.warning("[SPS30] Transient I2C error during read")
            else:
                logging.error(f"[SPS30] OS error reading data: {e}")
        except Exception as e:
            logging.error(f"[SPS30] Read failed: {e}")

        return data

    def stop(self):
        """
        Stop measurement.
        Only stops if currently started.
        """
        if not self.sensor or not self.is_started:
            return

        try:
            if self.mode == "i2c":
                self.sensor.stop_measurement()
            else:  # uart
                self.sensor.stopMeasurement()

            self.is_started = False

        except OSError as e:
            if e.errno == 121:  # Remote I/O error
                logging.warning("[SPS30] I2C error during stop (sensor may already be stopped)")
                self.is_started = False
            else:
                logging.error(f"[SPS30] OS error stopping: {e}")
        except Exception as e:
            logging.error(f"[SPS30] Stop failed: {e}")

    def is_ready(self):
        """Check if sensor is initialized and ready"""
        return self.sensor is not None

    def is_measuring(self):
        """Check if sensor is currently measuring"""
        return self.is_started

    def cleanup(self):
        """Cleanup resources - call this when shutting down"""
        if self.sensor and self.is_started:
            logging.info("[SPS30] Cleaning up - stopping measurement")
            self.stop()