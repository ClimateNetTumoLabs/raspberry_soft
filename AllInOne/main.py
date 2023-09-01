import time
from Sensors import AirQualitySensor, CO2Sensor, LightSensor, TPHSensor
from WeatherMeterSensors import WeatherSensors

times = {
    "Light": [],
    "TPH": [],
    "AirQuality": [],
    "CO2": [],
    "Weather": []
}

def main(light_obj, tph_obj, air_quality_obj, co2_obj, weather):
    global times

    data = {}

    start_time = time.time()
    data["Light"] = light_obj.read_data()
    times["Light"].append(time.time() - start_time)

    start_time = time.time()
    tph_data = tph_obj.read_data()
    data.update(tph_data)
    times["TPH"].append(time.time() - start_time)

    start_time = time.time()
    air_quality_data = air_quality_obj.read_data()
    data.update(air_quality_data)
    times["AirQuality"].append(time.time() - start_time)

    start_time = time.time()
    data["CO2"] = co2_obj.get_data()
    times["CO2"].append(time.time() - start_time)

    start_time = time.time()
    data.update(weather.get_data())
    times["Weather"].append(time.time() - start_time)

    return data


if __name__ == "__main__":
    light_obj = LightSensor() 
    tph_obj = TPHSensor()
    air_quality_obj = AirQualitySensor()
    co2_obj = CO2Sensor()
    weather = WeatherSensors()

    for i in range(10):
        air_quality_obj.read_data()
    j = 0
    while True:
        if j == 15:
            sum_avg = 0
            sum_max = 0
            for key, value in times.items():
                sum_avg += (sum(value) / len(value))
                sum_max += max(value)
                print(f"{key}  ->  {value}  ->  Max:{round(max(value), 2)}  ->  Average:{round(sum(value) / len(value), 2)}")
            print(f"Sum_Max  ->  {round(sum_max, 2)}")
            print(f"Sum_Avg  ->  {round(sum_avg, 2)}")
            print("\n" + ("#" * 50) + "\n")
            break

        data = main(light_obj, tph_obj, air_quality_obj, co2_obj, weather)

        for key, value in data.items():
            print(f"{key}: {value}")

        print("\n" + str(j) + ("#" * 50) + "\n")

        j += 1

