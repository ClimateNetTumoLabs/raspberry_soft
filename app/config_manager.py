import json
import os


class ConfigManager:
    """Manages configuration for ClimateNet sensors and system behavior."""

    def __init__(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            self.config = json.load(f)

        # Validate root fields
        self.sensors = self.config.get("sensors", {})
        self.transmission_interval_minutes = self.config.get("transmission_interval_minutes", 15)
        self.sampling_interval_seconds = self.config.get("sampling_interval_seconds", 30)
        self.averaging_window_minutes = self.config.get("averaging_window_minutes", 5)

    # ----------------------------------------------------------------------
    # --- SENSOR CONFIGS ---
    # ----------------------------------------------------------------------
    def get_sensor_config(self, sensor_name: str) -> dict:
        """Return full configuration dict for a given sensor."""
        sensor_cfg = self.sensors.get(sensor_name)
        if not sensor_cfg:
            raise KeyError(f"Sensor '{sensor_name}' not found in config.")
        return sensor_cfg

    def is_sensor_enabled(self, sensor_name: str) -> bool:
        """Check if sensor is enabled in configuration."""
        cfg = self.get_sensor_config(sensor_name)
        return cfg.get("enabled", True)

    # ----------------------------------------------------------------------
    # --- INTERVALS ---
    # ----------------------------------------------------------------------
    def get_sampling_interval(self) -> int:
        """Return sampling interval in seconds."""
        return self.sampling_interval_seconds

    def get_averaging_window(self) -> int:
        """Return averaging window in minutes."""
        return self.averaging_window_minutes

    def get_transmission_interval(self) -> int:
        """Return transmission interval in minutes."""
        return self.transmission_interval_minutes

    # ----------------------------------------------------------------------
    # --- UTILITIES ---
    # ----------------------------------------------------------------------
    def list_enabled_sensors(self):
        """Return a list of all enabled sensor names."""
        return [name for name, cfg in self.sensors.items() if cfg.get("enabled", True)]

    def list_all_sensors(self):
        """Return all sensor names regardless of enabled status."""
        return list(self.sensors.keys())

    def print_summary(self):
        """Print a quick overview of loaded configuration."""
        print("\n=== Configuration Summary ===")
        print(f"Sampling Interval: {self.sampling_interval_seconds}s")
        print(f"Averaging Window:  {self.averaging_window_minutes}min")
        print(f"Transmission Int.: {self.transmission_interval_minutes}min\n")

        for name, cfg in self.sensors.items():
            status = "ENABLED" if cfg.get("enabled", True) else "DISABLED"
            print(f" - {name}: {status}")
        print("=============================\n")
