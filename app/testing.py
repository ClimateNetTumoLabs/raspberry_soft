import os
import time

from prettytable import PrettyTable

import config
from scripts.change_permissions import chmod_tty
from scripts.network_checker import check_network
from scripts.rtc import RTCControl
from scripts.time_updater import update_rtc_time
from sensors.other_sensors.TPH_sensor_BME280 import TPHSensor
from sensors.other_sensors.air_quality_sensor_SPS30_i2c import AirQualitySensor
from sensors.other_sensors.light_sensor_LTR390 import LightSensor
from sensors.weather_meter_sensors.rain_sensor import Rain
from sensors.weather_meter_sensors.wind_direction_sensor import WindDirection
from sensors.weather_meter_sensors.wind_speed_sensor import WindSpeed


class TestSensors:
    """
    Class to test various sensors and display their status using PrettyTable.

    Attributes:
        light (LightSensor): Instance of LightSensor.
        tph (TPHSensor): Instance of TPHSensor.
        air_quality (AirQualitySensor): Instance of AirQualitySensor.
        rtc (RTCControl or None): Instance of RTCControl if available, otherwise None.
        wind_direction_sensor (WindDirection): Instance of WindDirection sensor.
        wind_speed_sensor (WindSpeed): Instance of WindSpeed sensor.
        rain_sensor (Rain): Instance of Rain sensor.
        results (dict): Dictionary to store test results.
    """

    def __init__(self) -> None:
        """
        Initializes sensor instances, sets up RTC if available, and initializes result tracking.
        """
        chmod_tty()
        self.light = LightSensor()
        self.tph = TPHSensor()
        self.air_quality = AirQualitySensor()
        try:
            self.rtc = RTCControl()
        except Exception:
            self.rtc = None

        self.wind_direction_sensor = WindDirection()
        self.wind_speed_sensor = WindSpeed()
        self.rain_sensor = Rain()
        os.system("clear")

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
            "Network": False,
            "RTC": False
        }

    def format_result(self, result) -> str:
        """
        Formats the result for display in PrettyTable.

        Args:
            result (any): Result to format.

        Returns:
            str: Formatted result.
        """
        os.system("clear")

        if isinstance(result, list) and len(result) > 1:
            is_success = result[0]
            formatted_data = result[1]

            if isinstance(formatted_data, dict):
                formatted_lines = []
                for key, value in formatted_data.items():
                    formatted_lines.append(f"{key}: {value}")
                formatted_data = '\n'.join(formatted_lines)

            return f"{is_success}\n\n{formatted_data}"

        return result

    def print_results(self) -> None:
        """
        Prints the current results using PrettyTable.
        """
        table = PrettyTable()
        table.field_names = ["Key", "Value"]

        for key, value in self.results.items():
            formatted_value = self.format_result(value)
            table.add_row([key, formatted_value], divider=True)

        table.align = "l"
        print(table)

    def speed_ok(self) -> None:
        """
        Handles the event when wind speed sensor is OK.
        """
        if not self.results["WindSpeed"]:
            self.results["WindSpeed"] = True
            self.print_results()

    def rain_ok(self) -> None:
        """
        Handles the event when rain sensor is OK.
        """
        if not self.results["Rain"]:
            self.results["Rain"] = True
            self.print_results()

    def check_devices(self) -> None:
        """
        Checks the status of all sensors and network connectivity.
        """
        res_light = self.light.read_data()
        if res_light:
            self.results["LightSensor"].append(res_light)
            for elem in res_light.values():
                if elem is None:
                    self.results["LightSensor"][0] = False
                    break
        else:
            self.results["LightSensor"] = False

        res_tph = self.tph.read_data()
        if res_tph:
            self.results["TPHSensor"].append(res_tph)
            for elem in res_tph.values():
                if elem is None:
                    self.results["TPHSensor"][0] = False
                    break
        else:
            self.results["TPHSensor"] = False
        self.air_quality.start()
        res_air_quality = self.air_quality.read_data()
        if res_air_quality:
            self.results["AirQualitySensor"].append(res_air_quality)
            for elem in res_air_quality.values():
                if elem is None:
                    self.results["AirQualitySensor"][0] = False
                    break
        else:
            self.results["AirQualitySensor"] = False
        self.air_quality.stop()

        res_wind_direction = self.wind_direction_sensor.read_data()
        self.results["WindDirection"].append(res_wind_direction)
        if res_wind_direction is None:
            self.results["WindDirection"][0] = False

        if check_network():
            self.results["Network"] = True

        if self.rtc is not None:
            try:
                res = update_rtc_time()
                if not res:
                    self.results["Network"] = False

                res_rtc = self.rtc.get_time()
                self.results["RTC"] = [True, res_rtc.strftime("%d-%m-%Y %H:%M:%S")]
            except Exception:
                self.results["RTC"] = False

        self.print_results()


test_sensors: TestSensors = TestSensors()
test_sensors.check_devices()

while True:
    time.sleep(1000)