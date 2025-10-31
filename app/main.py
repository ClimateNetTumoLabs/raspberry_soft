from sensors.climate_sensors.tph_bme280 import BME280Sensor
from sensors.climate_sensors.air_pollution_sps30 import SPS30Sensor
from sensors.climate_sensors.uv_ltr390 import LTR390Sensor
from sensors.weather_sensors.rain_sensor import RainSensor
from sensors.weather_sensors.wind_direction import WindDirectionSensor
from sensors.weather_sensors.wind_speed import WindSpeedSensor
import sys
import threading

def main():
    """Main entry point for reading all sensors and printing averaged results."""

    print("=== ClimateNet Station Data Collection ===")

    # Initialize sensors
    try:
        light_sensor = LTR390Sensor()
        tph_sensor = BME280Sensor()
        air_pollution_sensor = SPS30Sensor()
        rain_sensor = RainSensor()
        wind_speed = WindSpeedSensor()
        wind_direction = WindDirectionSensor()
    except Exception as e:
        print(f"[Init Error] Failed to initialize sensors: {e}")
        sys.exit(1)

    print("\nCollecting data...\n")

    threads = []
    results = {}

    def run_sensor(name, func):
        results[name] = func()

    # Create threads
    threads.append(threading.Thread(target=run_sensor, args=("bme", tph_sensor.average_values)))
    threads.append(threading.Thread(target=run_sensor, args=("ltr", light_sensor.average_values)))
    threads.append(threading.Thread(target=run_sensor, args=("sps", air_pollution_sensor.average_values)))
    threads.append(threading.Thread(target=run_sensor, args=("wind", wind_speed.average_speed)))
    threads.append(threading.Thread(target=run_sensor, args=("direction", wind_direction.average_direction)))
    threads.append(threading.Thread(target=run_sensor, args=("rain", rain_sensor.total_rainfall)))

    # Start all
    for t in threads:
        t.start()

    # Wait for all to finish
    for t in threads:
        t.join()

    # Merge results
    all_data = {}
    for data in results.values():
        all_data.update(data)


if __name__ == "__main__":
    main()
