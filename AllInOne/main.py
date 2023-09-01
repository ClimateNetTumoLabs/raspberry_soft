import time
from Sensors import AirQualitySensor, CO2Sensor, LightSensor, TPHSensor
from WeatherMeterSensors import WeatherSensors


def add_data(sensors):
    data = {}

    for sensor, name in sensors.items():
        res = sensor.read_data()
        if type(res) == dict:
            data.update(res)
        elif type(res) == int:
            data[name] = res
    
    return data


def get_averages(data, weather):
    result_data = {}
    for key, values in data.items():
        if key == "directory":
            result_data[key] = weather.get_direction_label(values)
        else:
            result_data[key] = round(sum(values) / len(values), 2)
        result_data[key]


def main(light_obj, tph_obj, air_quality_obj, co2_obj, weather):
    sensors = {
        light_obj: "Light",
        tph_obj: "",
        air_quality_obj: "",
        co2_obj: "CO2",
        weather: ""
    }

    data_all = {}

    start_time = time.time()

    while time.time() - start_time < 60:
        data = add_data(sensors)

        for key, value in data.items():
            if value is None:
                continue
            if key not in data_all:
                data_all[key] = [value, 1]
            else:
                data_all[key][0] += value
                data_all[key][1] += 1
        
        t = time.time() - start_time
        if 60 - t <= 25:
            time.sleep(60 - t)

    data_all["direction"] = data_all.get("direction")

    return data_all


if __name__ == "__main__":
    light_obj = LightSensor() 
    tph_obj = TPHSensor()
    air_quality_obj = AirQualitySensor()
    co2_obj = CO2Sensor()
    weather = WeatherSensors()

    for i in range(10):
        air_quality_obj.read_data()


    while True:
        data = main(light_obj, tph_obj, air_quality_obj, co2_obj, weather)

        for key, value in data.items():
            if key == "direction":
                direction = weather.get_direction_label(value)
                print(f"{key}: {direction}")
            else: 
                print(f"{key}: {round(value[0] / value[1], 2)}")
        print("\n" + ("#" * 50) + "\n")


