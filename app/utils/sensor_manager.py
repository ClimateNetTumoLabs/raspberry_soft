import datetime
import time
from collections import defaultdict
from metro_config import READING_TIME, SPS30_MIN_TEMPERATURE, SPS30_MAX_TEMPERATURE, SPS30_MAX_HUMIDITY
from version import __version__
from logger_config import logging
from sensors.read_sensors import sensors


PM_KEYS = ("pm1", "pm2_5", "pm10")


def within_sps30_limits(temperature, humidity) -> bool:
    """Unknown conditions count as outside: PM is only reported when they are known to be within limits."""
    if temperature is None or humidity is None:
        return False
    return SPS30_MIN_TEMPERATURE <= temperature <= SPS30_MAX_TEMPERATURE and humidity <= SPS30_MAX_HUMIDITY


class SensorManager:
    """Manages sensor initialization, data collection, and averaging"""

    def __init__(self):
        self.sensors = {}
        self.measurement_buffer = defaultdict(list)
        # Whether the SPS30 ran in the current window. Kept apart from the
        # sensor's own is_started, which stop_sensors() clears before averaging.
        self.sps30_started = False
        self._initialize_sensors()

    def _initialize_sensors(self):
        """Initialize all sensors from read_sensors.py"""
        for sensor_name, sensor_class in sensors.items():
            try:
                self.sensors[sensor_name] = sensor_class()
            except Exception as e:
                logging.error(f"✗ Failed to initialize {sensor_name}: {e}")

    def sps30(self):
        """The air quality sensor if it is an SPS30, else None (PMS5003 or no sensor)."""
        sensor = self.sensors.get("airQuality")
        mode = getattr(sensor, "mode", None) or ""
        return sensor if mode.startswith("sps30") else None

    def _sps30_conditions_ok(self) -> bool:
        """One BME280/SHT45 reading, taken before the SPS30 is started."""
        tph = self.sensors.get("tph")
        reading = tph.read_data() if tph else {}
        temperature, humidity = reading.get("temperature"), reading.get("humidity")

        if within_sps30_limits(temperature, humidity):
            return True

        logging.warning(
            f"[SPS30] Not started this window: temperature {temperature} °C, humidity {humidity} % "
            f"(limits {SPS30_MIN_TEMPERATURE}..{SPS30_MAX_TEMPERATURE} °C, <= {SPS30_MAX_HUMIDITY} %)"
        )
        return False

    def start_sensors(self):
        """Start sensors that need warmup (like SPS30)"""
        sps30 = self.sps30()

        for sensor_name, sensor_instance in self.sensors.items():
            if hasattr(sensor_instance, 'start') and sensor_name != "rain":
                if sensor_instance is sps30 and not self._sps30_conditions_ok():
                    continue
                try:
                    sensor_instance.start()
                except Exception as e:
                    logging.error(f"Error starting {sensor_name}: {e}")

        # A failed start counts as not started too.
        self.sps30_started = bool(sps30 and sps30.is_started)

    def stop_sensors(self):
        """Stop sensors after measurement period"""
        for sensor_name, sensor_instance in self.sensors.items():
            if hasattr(sensor_instance, 'stop') and sensor_name != "rain":
                try:
                    sensor_instance.stop()
                except Exception as e:
                    logging.error(f"Error stopping {sensor_name}: {e}")

    def collect_single_reading(self):
        """Collect one reading from all sensors (except rain)"""
        timestamp = datetime.datetime.now()
        sps30 = self.sps30()

        for sensor_name, sensor_instance in self.sensors.items():
            if sensor_name == "rain":  # Rain is handled separately
                continue
            if sensor_instance is sps30 and not self.sps30_started:
                continue  # not running this window, its PM is sent as null anyway
            try:
                data = sensor_instance.read_data()
                if data:
                    if isinstance(data, dict):
                        for key, value in data.items():
                            self.measurement_buffer[key].append(value)
                    else:
                        self.measurement_buffer[sensor_name].append(data)
            except Exception as e:
                logging.error(f"Error reading {sensor_name}: {e}")

    def start_measurement_period(self, start_time: datetime.datetime, end_time: datetime.datetime):
        """Collect readings every READING_TIME seconds until end_time"""
        self.measurement_buffer.clear()  # Clear previous data
        self.start_sensors()

        # Now start collecting readings
        logging.info("Beginning data collection...")
        next_reading = datetime.datetime.now()  # Start immediately after warmup

        while datetime.datetime.now() < end_time:
            now = datetime.datetime.now()

            if now >= next_reading:
                self.collect_single_reading()
                next_reading += datetime.timedelta(seconds=READING_TIME)

            time.sleep(0.5)  # Prevent busy loop

        # Stop sensors after measurement period
        self.stop_sensors()

    def calculate_averages(self):
        """Calculate averages from measurement buffer"""
        averages = {}

        for key, values in self.measurement_buffer.items():
            if not values:
                continue

            # Filter out None values for averaging
            valid_values = [v for v in values if v is not None]

            if not valid_values:
                # All values were None, keep as None
                averages[key] = None
                continue

            # For direction (compass), use most common value
            if key == "direction":
                averages[key] = max(set(valid_values), key=valid_values.count)
            else:
                # Numeric average
                try:
                    averages[key] = round(sum(valid_values) / len(valid_values), 2)
                except (TypeError, ValueError):
                    logging.warning(f"Could not average {key}: {values}")
                    averages[key] = None

        return averages

    def get_rain_data(self) -> float:
        """Get accumulated rain data"""
        if "rain" not in self.sensors:
            return 0.0
        try:
            rain_value = self.sensors["rain"].read_data()
            return rain_value if rain_value is not None else 0.0
        except Exception as e:
            logging.error(f"Error reading rain sensor: {e}")
            return 0.0

    def get_averaged_data(self, timestamp: datetime.datetime):
        """Prepare final data packet with averages and rain"""
        data = self.calculate_averages()
        data["rain"] = self.get_rain_data()

        # Only set direction to None if speed is 0, otherwise keep whatever direction value we have
        if data.get("speed") == 0 or data.get("speed") is None:
            data["direction"] = None

        self.apply_pm_limits(data)

        data["time"] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        # Stamped when measured, not when sent: a buffered record can go out
        # after the station has been updated.
        data["sw_version"] = __version__
        return data

    def apply_pm_limits(self, data: dict):
        """PM is null for a window the SPS30 did not run in, or whose averaged conditions were outside its limits."""
        if not self.sps30():
            return
        if self.sps30_started and within_sps30_limits(data.get("temperature"), data.get("humidity")):
            return
        for key in PM_KEYS:
            data[key] = None

    def cleanup(self):
        """Cleanup sensors if needed"""
        self.stop_sensors()
