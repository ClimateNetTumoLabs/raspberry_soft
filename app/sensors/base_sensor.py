import time
import statistics


class BaseSensor:
    """Generic sensor base class for sampling and averaging."""

    def __init__(self, config_manager, sensor_name):
        self.config = config_manager
        self.name = sensor_name

        sensor_config = self.config.get_sensor_config(sensor_name)
        self.enabled = sensor_config.get("enabled", True)

        if not self.enabled:
            print(f"[INFO] Sensor '{self.name}' is disabled in config.")
            return  # skip initialization

        self.measurements = sensor_config.get("measurements", [])

        # Config values
        self.sampling_interval = self.config.get_sampling_interval()
        self.averaging_window = self.config.get_averaging_window()
        self.transmission_interval = self.config.get_transmission_interval()

        # Derived
        self.window_seconds = self.averaging_window * 60
        self.samples = []  # list of (timestamp, measurement_dict)
        self.last_sample_time = 0
        self.last_transmit_time = 0

    # --- abstract method ---
    def _read_sensor(self):
        raise NotImplementedError("Subclasses must implement _read_sensor()")

    # --- main logic ---
    def measure(self, current_time):
        """Take a new measurement if sampling interval elapsed."""
        if current_time - self.last_sample_time >= self.sampling_interval:
            data = self._read_sensor()
            if data:
                self.samples.append((current_time, data))
                self.last_sample_time = current_time
                self.samples = [
                    (t, d) for (t, d) in self.samples if current_time - t <= self.window_seconds
                ]

    def get_average(self, current_time):
        """Compute average for last averaging window."""
        valid = [d for (t, d) in self.samples if current_time - t <= self.window_seconds]
        if not valid:
            return None
        avg = {}
        for key in valid[0].keys():
            avg[key] = statistics.mean([v[key] for v in valid])
        return avg

    def should_transmit(self, current_time):
        return current_time - self.last_transmit_time >= self.transmission_interval * 60

    def mark_transmitted(self, current_time):
        self.last_transmit_time = current_time
