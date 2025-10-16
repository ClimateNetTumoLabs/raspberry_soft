from config_manager import ConfigManager
from sensors.climate_sensors.thp_bme280 import BME280Sensor
from sensors.climate_sensors.air_pollution_sps30 import SPS30Sensor
from sensors.climate_sensors.uv_ltr390 import LTR390Sensor

# Initialize config
config = ConfigManager("config.json")
config.print_summary()

# Create sensors
bme = BME280Sensor(config)
sps = SPS30Sensor(config)
uv = LTR390Sensor(config)

# Example usage
import time
now = time.time()

for sensor in [bme, sps, uv]:
    if getattr(sensor, "enabled", False):
        sensor.measure(now)
        print(sensor.get_average(now))
