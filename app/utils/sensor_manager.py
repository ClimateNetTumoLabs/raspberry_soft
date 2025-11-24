import datetime
import time
from collections import defaultdict
from config import READING_TIME
from logger_config import logging
from sensors.read_sensors import sensors


class SensorManager:
    """Manages sensor initialization, data collection, and averaging"""

    def __init__(self):
        self.sensors = {}
        self.measurement_buffer = defaultdict(list)
        self._initialize_sensors()

    def _initialize_sensors(self):
        """Initialize all sensors from read_sensors.py"""
        for sensor_name, sensor_class in sensors.items():
            try:
                self.sensors[sensor_name] = sensor_class()
            except Exception as e:
                logging.error(f"✗ Failed to initialize {sensor_name}: {e}")

    def start_sensors(self):
        """Start sensors that need warmup (like SPS30)"""
        for sensor_name, sensor_instance in self.sensors.items():
            if hasattr(sensor_instance, 'start') and sensor_name != "rain":
                try:
                    sensor_instance.start()
                except Exception as e:
                    logging.error(f"Error starting {sensor_name}: {e}")

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

        for sensor_name, sensor_instance in self.sensors.items():
            if sensor_name == "rain":  # Rain is handled separately
                continue
            try:
                data = sensor_instance.read_data()
                if data:
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if value is not None:
                                self.measurement_buffer[key].append(value)
                    else:
                        self.measurement_buffer[sensor_name].append(data)
            except Exception as e:
                logging.error(f"Error reading {sensor_name}: {e}")

        logging.debug(f"Reading collected at {timestamp.strftime('%H:%M:%S')}")

    def start_measurement_period(self, start_time: datetime.datetime, end_time: datetime.datetime):
        """Collect readings every READING_TIME seconds until end_time"""
        self.measurement_buffer.clear()  # Clear previous data

        # Start sensors that need warmup (this will block during warmup)
        logging.info("Starting sensors and warming up...")
        self.start_sensors()

        # Now start collecting readings
        logging.info("Beginning data collection...")
        next_reading = datetime.datetime.now()  # Start immediately after warmup

        while datetime.datetime.now() < end_time:
            now = datetime.datetime.now()

            if now >= next_reading:
                self.collect_single_reading()
                next_reading += datetime.timedelta(seconds=READING_TIME)

        # Stop sensors after measurement period
        self.stop_sensors()

    def calculate_averages(self):
        """Calculate averages from measurement buffer"""
        averages = {}

        for key, values in self.measurement_buffer.items():
            if not values:
                continue

            # For direction (compass), use most common value
            if key == "direction":
                averages[key] = max(set(values), key=values.count)
            else:
                # Numeric average
                try:
                    averages[key] = round(sum(values) / len(values), 2)
                except (TypeError, ValueError):
                    logging.warning(f"Could not average {key}: {values}")

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
        if data["speed"] == 0:
            data["direction"] = None
        data["time"] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return data

    def cleanup(self):
        """Cleanup sensors if needed"""
        self.stop_sensors()