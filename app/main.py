import asyncio
from config import MEASURING_TIME, TRANSMISSION_INTERVAL, DEVICE_ID
from sensors.climate_sensors.tph_bme280 import BME280Sensor
from sensors.climate_sensors.air_pollution_sps30 import SPS30Sensor
from sensors.climate_sensors.uv_ltr390 import LTR390Sensor
from sensors.weather_sensors.rain_sensor import RainSensor
from sensors.weather_sensors.wind_direction import WindDirectionSensor
from sensors.weather_sensors.wind_speed import WindSpeedSensor
from data.checkings import EdgeDataManager
from logger_config import logging

async def measure_and_send(edge_manager, sensors):
    """Measures all sensors and sends via EdgeDataManager."""
    tph_sensor, light_sensor, air_pollution_sensor, rain_sensor, wind_speed_sensor, wind_direction_sensor = sensors

    # Run all sensors concurrently
    results = await asyncio.gather(
        tph_sensor.average_values(),
        light_sensor.average_values(),
        air_pollution_sensor.average_values(),
        wind_speed_sensor.average_speed(),
        wind_direction_sensor.average_direction(),
        rain_sensor.total_rainfall()
    )

    measurement_time = edge_manager.get_rtc_time()

    speed = results[3]
    direction = results[4] if speed > 0 else None

    payload = {
        "time": measurement_time.strftime("%Y-%m-%d %H:%M:%S"),
        "uv": results[1]["uv"],
        "lux": results[1]["lux"],
        "temperature": results[0]["temperature"],
        "pressure": results[0]["pressure"],
        "humidity": results[0]["humidity"],
        "pm1": results[2]["pm1"],
        "pm2_5": results[2]["pm2_5"],
        "pm10": results[2]["pm10"],
        "speed": speed,
        "rain": results[5],
        "direction": direction
    }

    data_to_send = {
        "device": f"device{DEVICE_ID}",
        "data": [payload]
    }

    edge_manager.publish(data_to_send)
    logging.info(f"Measurement finished at {measurement_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Payload: {payload}")


async def main_loop():
    edge_manager = EdgeDataManager()

    # Initialize sensors once
    sensors = (
        BME280Sensor(),
        LTR390Sensor(),
        SPS30Sensor(),
        RainSensor(),
        WindSpeedSensor(),
        WindDirectionSensor()
    )

    while True:
        now = edge_manager.get_rtc_time()
        seconds_since_epoch = now.timestamp()

        # Find the next aligned transmission time (x:00, x:10, etc.)
        next_tx_epoch = ((seconds_since_epoch // TRANSMISSION_INTERVAL) + 1) * TRANSMISSION_INTERVAL
        measurement_start_epoch = next_tx_epoch - MEASURING_TIME

        # If we already passed measurement start, skip to the next full cycle
        if seconds_since_epoch >= measurement_start_epoch:
            next_tx_epoch += TRANSMISSION_INTERVAL
            measurement_start_epoch = next_tx_epoch - MEASURING_TIME

        wait_seconds = measurement_start_epoch - seconds_since_epoch
        logging.info(
            f"Waiting {wait_seconds:.1f}s to start measurement )")
        await asyncio.sleep(wait_seconds)

        logging.info("+++++++++++++++ Starting measurements...")
        await measure_and_send(edge_manager, sensors)

        # ✅ Now just naturally loop again — it will recalc next start correctly
        # No need for extra sleep here!


if __name__ == "__main__":
    asyncio.run(main_loop())