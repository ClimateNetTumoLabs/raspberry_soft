import time
from Sensors.WeatherMeterSensors import *
from Sensors.OtherSensors import *
from Scripts.rtc import RTCControl
import config
import os


class TestSensors:
    def __init__(self) -> None:
        self.light = LightSensor(testing=True)
        self.tph = TPHSensor(testing=True)
        self.air_quality = AirQualitySensor(testing=True)
        try:
            self.rtc = RTCControl()
        except Exception:
            self.rtc = None

        self.wind_direction_sensor = WindDirection(testing=True)
        self.wind_speed_sensor = WindSpeed()
        self.rain_sensor = Rain()

        if config.SENSORS["wind_speed"]["working"]:
            self.wind_speed_sensor.sensor.when_pressed = self.speed_ok

        if config.SENSORS["rain"]["working"]:
            self.rain_sensor.sensor.when_pressed = self.rain_ok

        self.results = {
            "LightSensor": [True],
            "TPHSensor": [True],
            "AirQualitySensor": [True],
            "WindDirection": [True],
            "WindSpeed": False,
            "Rain": False,
            "RTC": False
        }

    def print_res(self):
        os.system("clear")
        for key, value in self.results.items():
            print(f"{key}  ->  {value}")

    def speed_ok(self):
        self.results["WindSpeed"] = True
        self.print_res()

    def rain_ok(self):
        self.results["Rain"] = True
        self.print_res()

    def check_devices(self):
        res_light = self.light.read_data()
        self.results["LightSensor"].append(res_light)

        for elem in res_light.values():
            if elem is None:
                self.results["LightSensor"][0] = False
                break

        res_tph = self.tph.read_data()
        self.results["TPHSensor"].append(res_tph)
        for elem in res_tph.values():
            if elem is None:
                self.results["TPHSensor"][0] = False
                break

        res_air_quality = self.air_quality.read_data()
        self.results["AirQualitySensor"].append(res_air_quality)
        for elem in res_air_quality.values():
            if elem is None:
                self.results["AirQualitySensor"][0] = False
                break

        res_wind_direction = self.wind_direction_sensor.read_data()
        self.results["WindDirection"].append(res_wind_direction)
        if res_wind_direction is None:
            self.results["WindDirection"][0] = False

        if self.rtc is not None:
            try:
                res_rtc = self.rtc.get_time()
                self.results["RTC"] = [True, res_rtc.strftime("%d-%m-%Y %H:%M:%S")]
            except Exception:
                self.results["RTC"] = False

        self.print_res()


a = TestSensors()

a.check_devices()

while True:
    time.sleep(1000)
