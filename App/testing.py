import time
from Sensors.WeatherMeterSensors import *
from Sensors.OtherSensors import *
from Scripts.rtc import RTCControl
from Scripts.network_checker import check_network
from Scripts.time_updater import update_rtc_time
from Scripts import chmod_tty
from prettytable import PrettyTable
import config
import os


class TestSensors:
    """
    TestSensors class is responsible for testing various sensors and network connectivity.

    It initializes sensor objects and checks their functionality, updating the results in a dictionary.

    Attributes:
        light (LightSensor): Instance of the LightSensor class for testing light sensor.
        tph (TPHSensor): Instance of the TPHSensor class for testing temperature, pressure, and humidity sensor.
        air_quality (AirQualitySensor): Instance of the AirQualitySensor class for testing air quality sensor.
        rtc (RTCControl): Instance of the RTCControl class for handling real-time clock functionality.
        wind_direction_sensor (WindDirection): Instance of the WindDirection class for testing wind direction sensor.
        wind_speed_sensor (WindSpeed): Instance of the WindSpeed class for testing wind speed sensor.
        rain_sensor (Rain): Instance of the Rain class for testing rain sensor.
        results (dict): Dictionary to store test results of sensors and network connectivity.

    Methods:
        format_result(result): Formats the test result for better readability.
        print_results(): Prints the test results in a formatted table.
        speed_ok(): Callback function to handle successful wind speed sensor test.
        rain_ok(): Callback function to handle successful rain sensor test.
        check_devices(): Checks the functionality of all sensors and updates test results.

    """

    def __init__(self) -> None:
        """
        Initializes TestSensors class.

        Initializes sensor objects for testing various environmental sensors.
        Checks network connectivity.
        """
        chmod_tty()
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

    def format_result(self, result):
        """
        Formats the test result for better readability.

        Args:
            result: Test result to be formatted.

        Returns:
            str: Formatted test result.
        """
        os.system("clear")

        if isinstance(result, list):
            is_success, formatted_data = result

            if isinstance(formatted_data, dict):
                d = []
                for key, value in formatted_data.items():
                    d.append(f"{key}: {value}")
                formatted_data = '\n'.join(d)

            return f"{is_success}\n\n{formatted_data}"
        else:
            return result

    def print_results(self):
        """
        Prints the test results in a formatted table.
        """
        table = PrettyTable()
        table.field_names = ["Key", "Value"]

        for key, value in self.results.items():
            formatted_value = self.format_result(value)
            table.add_row([key, formatted_value], divider=True)

        table.align = "l"

        print(table)

    def speed_ok(self):
        """
        Callback function to handle successful wind speed sensor test.
        """
        if not self.results["WindSpeed"]:
            self.results["WindSpeed"] = True
            self.print_results()

    def rain_ok(self):
        """
        Callback function to handle successful rain sensor test.
        """
        if not self.results["Rain"]:
            self.results["Rain"] = True
            self.print_results()

    def check_devices(self):
        """
        Checks the functionality of all sensors and updates test results.

        Updates test results dictionary with the status of each sensor and network connectivity.
        """
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


a = TestSensors()

a.check_devices()

while True:
    time.sleep(1000)
