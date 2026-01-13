from config import SENSORS
from logger_config import logging
from .libs.PMS5003_lib import PMS5003


class PMS5003Sensor:
    def __init__(self) -> None:
        """
        Initializes the AirQualitySensor instance.
        """
        self.sensor = None
        self.conf = SENSORS["pms5003"]
        self.working = self.conf["working"]

        if self.working:
            self.setup_sensor()

    def setup_sensor(self) -> bool:
        try:
            sensor = PMS5003(
                device=self.conf["address"],
                baudrate=self.conf["baudrate"]
            )
            self.sensor = sensor
        except Exception as e:
            logging.error(f"[PMS5003] Start failed: {e}")

        return self.sensor is not None

    def stop(self) -> None:
        try:
            self.sensor.stop()
        except Exception as e:
            logging.error(f"Error occurred during stopping PMS5003 sensor: {e}")

    def read_data(self) -> dict:
        data = {"pm1": None, "pm2_5": None, "pm10": None}

        if self.working:
            if self.sensor is None or self.sensor.get_pin_state() == "LOW":
                if not self.setup_sensor():
                    return data

            try:
                all_data = self.sensor.read()
                data["pm1"] = all_data.pm_ug_per_m3(size=1.0, atmospheric_environment=True)
                data["pm2_5"] = all_data.pm_ug_per_m3(size=2.5, atmospheric_environment=True)
                data["pm10"] = all_data.pm_ug_per_m3(size=10, atmospheric_environment=True)
            except Exception as e:
                logging.error(f"Exception while reading PMS5003: {e}")

        return data