from sensors.climate_sensors.tph_bme280 import BME280Sensor
from sensors.climate_sensors.air_pollution_sps30 import SPS30Sensor
from sensors.climate_sensors.uv_ltr390 import LTR390Sensor
from sensors.weather_sensors.rain_sensor import RainSensor
from sensors.weather_sensors.wind_direction import WindDirectionSensor
from sensors.weather_sensors.wind_speed import WindSpeedSensor
import sys

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

    # Measure all sensors
    try:
        ltr_data = light_sensor.average_values()
        bme_data = tph_sensor.average_values()
        sps_data = air_pollution_sensor.average_values()
        wind_data = wind_speed.average_speed()
        direction_data = wind_direction.average_direction()
        rain_data = rain_sensor.total_rainfall()
    except Exception as e:
        print(f"[Measurement Error] {e}")
        sys.exit(1)

    # Combine results
    all_data = {
        **bme_data,
        **ltr_data,
        **sps_data,
        **wind_data,
        **rain_data,
        **direction_data
    }

    print("\n=== Averaged Sensor Results ===")
    for key, value in all_data.items():
        print(f"{key}: {value}")

    print("\nData collection complete.")


if __name__ == "__main__":
    main()
