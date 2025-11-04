import asyncio
import time
from sensors.climate_sensors.tph_bme280 import BME280Sensor
from sensors.climate_sensors.air_pollution_sps30 import SPS30Sensor
from sensors.climate_sensors.uv_ltr390 import LTR390Sensor
from sensors.weather_sensors.rain_sensor import RainSensor
from sensors.weather_sensors.wind_direction import WindDirectionSensor
from sensors.weather_sensors.wind_speed import WindSpeedSensor

async def main():
    """Main entry point: measure all sensors concurrently and print results."""
    print("=== ClimateNet Station Data Collection ===\n")

    # Initialize sensors
    light_sensor = LTR390Sensor()
    tph_sensor = BME280Sensor()
    air_pollution_sensor = SPS30Sensor()
    rain_sensor = RainSensor()
    wind_speed_sensor = WindSpeedSensor()
    wind_direction_sensor = WindDirectionSensor()

    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] Measurement started at {start_time}\n")
    print("Collecting data...\n")

    # Run all sensors concurrently
    results = await asyncio.gather(
        tph_sensor.average_values(),
        light_sensor.average_values(),
        air_pollution_sensor.average_values(),
        wind_speed_sensor.average_speed(),
        wind_direction_sensor.average_direction(),
        rain_sensor.total_rainfall()
    )

    # Merge results
    all_data = {
        "[BME280]": results[0],
        "[LTR390]": results[1],
        "[SPS30]": results[2],
        "[Wind Speed]": results[3],
        "[Wind Direction]": results[4],  # only compass direction string
        "[Rain]": results[5]
    }

    end_time = time.strftime("%Y-%m-%d %H:%M:%S")
    print("=== Averaged Sensor Data ===")
    for key, value in all_data.items():
        print(f"{key}: {value}")
    print(f"\n[LOG] Measurement finished at {end_time}")


if __name__ == "__main__":
    asyncio.run(main())
