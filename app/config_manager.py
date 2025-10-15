import yaml
from pathlib import Path


class ConfigManager:
    def __init__(self, path="config.yaml"):
        self.path = Path(path)
        self.config = self._load_config()

    def _load_config(self):
        with open(self.path, "r") as f:
            return yaml.safe_load(f)

    def get_sampling_interval(self):
        return self.config["sampling_interval_seconds"]

    def get_averaging_window(self):
        return self.config["averaging_window_minutes"]

    def get_transmission_interval(self):
        return self.config["transmission_interval_minutes"]

    def get_sensor_config(self, sensor_name):
        return self.config["sensors"].get(sensor_name, {})
