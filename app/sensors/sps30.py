import time
from sps30 import SPS30 as SPS30I2C
from config import SENSORS
from logger_config import logging
from .SPS30_lib import SPS30 as SPS30UART


class SPS30Sensor:
    def __init__(self):
        self.sensor = None
        self.mode = None

        conf = SENSORS["sps30"]
        self.warmup_time = conf["warmup"]

        if conf["i2c"]["working"]:
            self.setup_i2c(conf["i2c"])

        if conf["uart"]["working"] and self.sensor is None:
            self.setup_uart(conf["uart"])

        if not self.sensor:
            logging.error("[SPS30] No working mode found")
            return

        self.start()

    def setup_i2c(self, conf):
        try:
            port = conf["port"]
            sensor = SPS30I2C(port)

            if sensor.read_article_code() == sensor.ARTICLE_CODE_ERROR:
                raise RuntimeError("CRC ERROR on I2C")

            self.sensor = sensor
            self.mode = "i2c"
            logging.info("[SPS30] Using I2C mode")

        except Exception as e:
            logging.error(f"[SPS30] I2C init failed: {e}")

    def setup_uart(self, conf):
        try:
            address = conf["address"]
            baudrate = conf["baudrate"]
            timeout = conf["timeout"]
            sensor = SPS30UART(address, baudrate, timeout)
            sensor.resetDevice()
            self.sensor = sensor
            self.mode = "uart"
            logging.info("[SPS30] Using UART mode")

        except Exception as e:
            logging.error(f"[SPS30] UART init failed: {e}")

    def start(self):
        if not self.sensor:
            return

        try:
            if self.mode == "i2c":
                self.sensor.start_measurement()

            elif self.mode == "uart":
                # THIS IS REQUIRED FOR UART MODE
                self.sensor.startMeasurement()

            logging.info(f"[SPS30] Warming up for {self.warmup_time}s")
            time.sleep(self.warmup_time)

        except Exception as e:
            logging.error(f"[SPS30] Error during start: {e}", exc_info=True)


    def read_data(self):
        data = {"pm1": None, "pm2_5": None, "pm10": None}

        if not self.sensor:
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

        except Exception as e:
            logging.error(f"[SPS30] Failed to read data ({self.mode}): {e}")

        return data


    def stop(self):
        if self.sensor:
            try:
                if self.mode == "i2c":
                    self.sensor.stop_measurement()
                elif self.mode == "uart":
                    self.sensor.stopMeasurement()
            except Exception as e:
                logging.error(f"Couldn't stop [SPS3 {self.mode}]", e)

