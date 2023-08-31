from Sensors import AirQualitySensor, CO2Sensor, LightSensor, TPHSensor
from WeatherMeterSensors import WeatherSensors

def main(light_obj, tph_obj, air_quality_obj, co2_obj, weather):
    data = {}
    
    data["Light"] = light_obj.read_data()
    
    tph_data = tph_obj.read_data()
    data.update(tph_data)

    air_quality_data = air_quality_obj.read_data()
    data.update(air_quality_data)

    data["CO2"] = co2_obj.get_data()

    data.update(weather.get_data())
    
    return data


if __name__ == "__main__":
    light_obj = LightSensor() 
    tph_obj = TPHSensor()
    air_quality_obj = AirQualitySensor()
    co2_obj = CO2Sensor()
    weather = WeatherSensors()

    while True:
        data = main(light_obj, tph_obj, air_quality_obj, co2_obj, weather)

        for key, value in data.items():
            print(f"{key}: {value}")

        print("\n" + ("#" * 50) + "\n")

