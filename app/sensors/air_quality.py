import time
from config import SENSORS
from metro_config import SPS30_WARMUP, SPS30_PM10_GSD
from logger_config import logging
from .libs.SPS30_I2C import SPS30 as SPS30I2C
from .libs.SPS30_UART import SPS30 as SPS30UART
from .libs.PMS5003 import PMS5003
from .pm10_model import pm10_from_tps


class AirQualitySensor:
    """
    Unified class for SPS30 (UART/I2C) and PMS5003.
    Selects automatically based on config and fallback.
    """

    def __init__(self):
        self.sensor = None
        self.mode = None      # sps30_i2c / sps30_uart / pms5003
        self.is_started = False

        self.conf_pms = SENSORS["pms5003"]
        self.conf_sps = SENSORS["sps30"]

        # Try PMS5003 first if enabled
        if self.conf_pms["working"]:
            if self._setup_pms():
                logging.info("[AirQuality] Using PMS5003")
                return

        # If PMS disabled or not working → try SPS30
        if self.conf_sps["uart"]["working"] or self.conf_sps["i2c"]["working"]:
            if self._setup_sps():
                logging.info("[AirQuality] Using SPS30")
                return

        logging.error("[AirQuality] No air quality sensor available")

    def _setup_pms(self):
        try:
            self.sensor = PMS5003(
                device=self.conf_pms["address"],
                baudrate=self.conf_pms["baudrate"]
            )
            self.mode = "pms5003"
            return True

        except Exception as e:
            logging.error(f"[PMS5003] Init failed: {e}")
            self.sensor = None
            return False

    def _setup_sps(self):
        conf = self.conf_sps

        # Determine priority (default UART first)
        if conf["i2c"]["working"] and not conf["uart"]["working"]:
            priority = ["i2c"]
        elif conf["uart"]["working"] and not conf["i2c"]["working"]:
            priority = ["uart"]
        else:
            priority = ["uart", "i2c"]

        for mode in priority:
            if mode == "i2c" and self._setup_sps_i2c(conf["i2c"]):
                return True
            if mode == "uart" and self._setup_sps_uart(conf["uart"]):
                return True

        return False

    def _setup_sps_i2c(self, conf):
        try:
            sensor = SPS30I2C(conf["port"])
            article_code = sensor.read_article_code()
            if article_code == sensor.ARTICLE_CODE_ERROR:
                raise RuntimeError("CRC ERROR on SPS30 I2C")

            self.sensor = sensor
            self.mode = "sps30_i2c"
            return True

        except Exception as e:
            logging.error(f"[SPS30] I2C init failed: {e}")
            self.sensor = None
            return False

    def _setup_sps_uart(self, conf):
        try:
            sensor = SPS30UART(conf["address"], conf["baudrate"], conf["timeout"])
            sensor.resetDevice()
            if not sensor.readDeviceInfo():
                raise RuntimeError("No response from SPS30 UART")

            self.sensor = sensor
            self.mode = "sps30_uart"
            return True

        except Exception as e:
            logging.error(f"[SPS30] UART init failed: {e}")
            self.sensor = None
            return False

    def start(self):
        if not self.sensor or self.is_started:
            return

        if self.mode.startswith("sps30"):
            try:
                if self.mode == "sps30_i2c":
                    self.sensor.start_measurement()
                else:
                    self.sensor.startMeasurement()

                self.is_started = True

                warmup = SPS30_WARMUP
                logging.info(f"[SPS30] Warming up for {warmup}s...")
                time.sleep(warmup)

            except Exception as e:
                logging.error(f"[SPS30] Start failed: {e}")
                self.is_started = False

    def read_data(self):
        # pm10 is corrected from the typical particle size (pm10_model.py); pm10_raw is the SPS30's own.
        # nc* are particle counts in #/cm3 from 0.3 um up to that size, tps the typical particle size in um.
        data = {"pm1": None, "pm2_5": None, "pm10": None, "pm10_raw": None,
                "nc0_5": None, "nc1": None, "nc2_5": None, "nc4": None, "nc10": None, "tps": None}

        if not self.sensor:
            return data

        try:
            if self.mode == "pms5003":
                frame = self.sensor.read()
                data["pm1"] = frame.pm_ug_per_m3(size=1.0, atmospheric_environment=True)
                data["pm2_5"] = frame.pm_ug_per_m3(size=2.5, atmospheric_environment=True)
                data["pm10"] = frame.pm_ug_per_m3(size=10, atmospheric_environment=True)

            elif self.mode == "sps30_i2c":
                if not self.sensor.read_data_ready_flag():
                    return data

                result = self.sensor.read_measured_values()
                if result == self.sensor.MEASURED_VALUES_ERROR:
                    logging.warning("[SPS30] Measurement CRC error")
                    return data

                vals = self.sensor.dict_values
                self._fill_sps30(data, vals["pm1p0"], vals["pm2p5"], vals["pm10p0"],
                                 vals["nc0p5"], vals["nc1p0"], vals["nc2p5"], vals["nc4p0"], vals["nc10p0"],
                                 vals["typical"])

            elif self.mode == "sps30_uart":
                vals = self.sensor.readMeasurement()
                if vals:
                    self._fill_sps30(data, vals["Mass PM1.0"], vals["Mass PM2.5"], vals["Mass PM10"],
                                     vals["Number PM0.5"], vals["Number PM1.0"], vals["Number PM2.5"],
                                     vals["Number PM4.0"], vals["Number PM10"], vals["Particle Size"])

        except Exception as e:
            logging.error(f"[AirQuality] Read failed: {e}")

        return data

    @staticmethod
    def _fill_sps30(data, pm1, pm25, pm10, nc05, nc1, nc25, nc4, nc10, tps):
        """Same output for I2C and UART. PM10 is corrected before rounding, so TPS keeps full precision."""
        data["pm1"], data["pm2_5"], data["pm10_raw"] = round(pm1, 2), round(pm25, 2), round(pm10, 2)
        data["pm10"] = round(pm10_from_tps(pm25, pm10, tps, SPS30_PM10_GSD), 2)
        data["nc0_5"], data["nc1"], data["nc2_5"] = round(nc05, 2), round(nc1, 2), round(nc25, 2)
        data["nc4"], data["nc10"], data["tps"] = round(nc4, 2), round(nc10, 2), round(tps, 3)

    def stop(self):
        if not self.sensor or not self.is_started:
            return

        if self.mode.startswith("sps30"):
            try:
                if self.mode == "sps30_i2c":
                    self.sensor.stop_measurement()
                else:
                    self.sensor.stopMeasurement()
            except Exception as e:
                logging.error(f"[SPS30] Stop failed: {e}")

        self.is_started = False

    def cleanup(self):
        try:
            self.stop()
        except Exception:
            pass
