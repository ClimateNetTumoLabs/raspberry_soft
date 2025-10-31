from sensors.climate_sensors.tph_bme280 import BME280Sensor
from sensors.climate_sensors.air_pollution_sps30 import SPS30Sensor
from sensors.climate_sensors.uv_ltr390 import LTR390Sensor
from sensors.weather_sensors.rain_sensor import RainSensor
from sensors.weather_sensors.wind_direction import WindDirectionSensor
from sensors.weather_sensors.wind_speed import WindSpeedSensor
import sys
import traceback


def main():
    """Main entry point for reading all sensors and printing averaged results."""
    print("=== ClimateNet Station Data Collection ===")

    sensors = {}
    failed_sensors = {}

    # === Initialize each sensor separately ===
    for name, cls in {
        "UV_LTR390": LTR390Sensor,
        "BME280": BME280Sensor,
        "SPS30": SPS30Sensor,
        "Rain": RainSensor,
        "WindSpeed": WindSpeedSensor,
        "WindDirection": WindDirectionSensor,
    }.items():
        try:
            print(f"\n[Init] Initializing {name}...")
            sensors[name] = cls()
        except Exception as e:
            print(f"[Init Error] {name} failed: {e}")
            traceback.print_exc(limit=1)
            failed_sensors[name] = str(e)

    # === If all failed ===
    if not sensors:
        print("\n❌ No sensors initialized successfully. Exiting.")
        sys.exit(1)

    print("\n✅ Initialization complete.\nCollecting data...\n")

    # === Measure each sensor separately ===
    results = {}
    for name, sensor in sensors.items():
        try:
            print(f"[Measure] Measuring {name}...")
            if name == "UV_LTR390":
                results.update(sensor.average_values())
            elif name == "BME280":
                results.update(sensor.average_values())
            elif name == "SPS30":
                results.update(sensor.average_values())
            elif name == "WindSpeed":
                results.update(sensor.average_speed())
            elif name == "WindDirection":
                results.update(sensor.average_direction())
            elif name == "Rain":
                results.update(sensor.total_rainfall())
        except Exception as e:
            print(f"[Measurement Error] {name}: {e}")
            traceback.print_exc(limit=1)
            failed_sensors[name] = str(e)

    # === Print all results ===
    print("\n=== Averaged Sensor Results ===")
    for key, value in results.items():
        print(f"{key}: {value}")

    if failed_sensors:
        print("\n⚠️ Some sensors failed:")
        for name, err in failed_sensors.items():
            print(f" - {name}: {err}")

    print("\n✅ Data collection complete.")


if __name__ == "__main__":
    main()
