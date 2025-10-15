import time
from config_manager import ConfigManager
from climate_sensors.thp_bme280 import BME280Sensor
from climate_sensors.air_pollution_sps30 import SPS30Sensor
from climate_sensors.uv_ltr390 import LTR390Sensor
from weather_sensors.wind_sensor import WindSensor
from weather_sensors.rain_sensor import RainGauge


def main():
    config = ConfigManager("config.yaml")

    sensors = [
        BME280Sensor(config),
        SPS30Sensor(config),
        LTR390Sensor(config),
        WindSensor(config),
        RainGauge(config),
    ]

    print("Running all sensors... (Ctrl+C to stop)")
    while True:
        now = time.time()

        for sensor in sensors:
            sensor.measure(now)
            if sensor.should_transmit(now):
                avg = sensor.get_average(now)
                if avg:
                    print(f"[{time.strftime('%H:%M:%S')}] {sensor.name}: {avg}")
                sensor.mark_transmitted(now)

        time.sleep(1)  # small loop delay for CPU efficiency


if __name__ == "__main__":
    main()
