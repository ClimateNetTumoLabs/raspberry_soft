import time
from Sensors import AirQualitySensor, CO2Sensor, LightSensor, TPHSensor
from WeatherMeterSensors import WeatherSensors


def read_sensor_data(sensor_name_map: dict) -> dict:
    sensor_data = {}

    for sensor, name in sensor_name_map.items():
        result = sensor.read_data()
        if isinstance(result, dict):
            sensor_data.update(result)
        elif isinstance(result, int):
            sensor_data[name] = result

    return sensor_data


def add_data(data_all: dict, sensors_data: dict) -> dict:
    for key, value in sensors_data.items():
        if value is None:
            continue
        if key not in data_all:
            data_all[key] = [value, 1]
        else:
            data_all[key][0] += value
            data_all[key][1] += 1
    return data_all


def get_averages(data_all: dict, weather_sensor: WeatherSensors) -> dict:
    result_data = {}
    for key, values in data_all.items():
        if key == "direction":
            result_data[key] = weather_sensor.get_direction_label(values)
        else:
            result_data[key] = round(sum(values) / len(values), 2)
    return result_data


def main(light_sensor: LightSensor, tph_sensor: TPHSensor, air_quality_sensor: AirQualitySensor, co2_sensor: CO2Sensor,
         weather_sensor: WeatherSensors) -> dict:
    sensor_name_map = {
        light_sensor: "Light",
        tph_sensor: "",
        air_quality_sensor: "",
        co2_sensor: "CO2",
        weather_sensor: ""
    }

    data_all = {}

    start_time = time.time()

    while time.time() - start_time < 60:
        sensor_data = read_sensor_data(sensor_name_map)
        data_all = add_data(data_all, sensor_data)

        remaining_time = 60 - (time.time() - start_time)
        if remaining_time <= 25:
            time.sleep(remaining_time)

    data_all["direction"] = data_all.get("direction")

    return get_averages(data_all, weather_sensor)


if __name__ == "__main__":
    light_sensor = LightSensor()
    tph_sensor = TPHSensor()
    air_quality_sensor = AirQualitySensor()
    co2_sensor = CO2Sensor()
    weather_sensor = WeatherSensors()

    while True:
        data = main(light_sensor, tph_sensor, air_quality_sensor, co2_sensor, weather_sensor)

        for key, value in data.items():
            print(f"{key}: {value}")
        print("\n" + ("#" * 50) + "\n")
