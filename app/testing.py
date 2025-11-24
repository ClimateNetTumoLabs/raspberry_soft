import os
import time
from prettytable import PrettyTable
from sensors.read_sensors import sensors
from utils.rtc import RTCControl
from utils.network import check_internet
from config import SENSORS
import warnings

warnings.filterwarnings("ignore", message="Falling back from lgpio", module="gpiozero.devices")


class TestSensors:
    def __init__(self):
        os.system("clear")

        # Initialize sensors
        self.sensor_instances = {}
        for name, cls in sensors.items():
            try:
                self.sensor_instances[name] = cls()
            except Exception as e:
                print(f"Failed to init {name}: {e}")

        # RTC
        try:
            self.rtc = RTCControl()
        except Exception:
            self.rtc = None

        # Results dictionary
        self.results = {
            "tph": [True],          # BME280
            "light": [True],        # LTR390
            "airQuality": [True],   # SPS30
            "direction": [True],
            "speed": [False],       # actual wind speed
            "rain": [False],        # rain count or status
            "Network": False,
            "RTC": False
        }

    def format_result(self, result):
        os.system("clear")
        if isinstance(result, list):
            if len(result) > 1:
                is_success = result[0]
                data = result[1]
                if isinstance(data, dict):
                    formatted_lines = [f"{k}: {v}" for k, v in data.items()]
                    data = "\n".join(formatted_lines)
                return f"{is_success}\n\n{data}"
            return result[0]
        return result

    def print_results(self):
        table = PrettyTable()
        table.field_names = ["Key", "Value"]
        for key, value in self.results.items():
            formatted_value = self.format_result(value)
            table.add_row([key, formatted_value], divider=True)
        table.align = "l"
        print(table)

    def check_devices(self):
        # Start SPS30 if present
        if "airQuality" in self.sensor_instances:
            try:
                self.sensor_instances["airQuality"].start()
            except:
                pass

        # Loop through sensors
        for name, instance in self.sensor_instances.items():
            try:
                res = instance.read_data()
                if res:
                    if name not in self.results:
                        self.results[name] = [True]
                    self.results[name].append(res)
                    # mark False if any reading is None
                    if isinstance(res, dict) and any(v is None for v in res.values()):
                        self.results[name][0] = False
                    elif res is None:
                        self.results[name][0] = False
                    else:
                        # For wind speed, store the numeric value directly
                        if name == "speed":
                            self.results["speed"] = [True, res]
                        # For rain, could store count or boolean
                        if name == "rain":
                            self.results["rain"] = [True, res]
                else:
                    self.results[name][0] = False
            except Exception:
                self.results[name][0] = False

        # Network check
        self.results["Network"] = check_internet()

        # RTC check
        if self.rtc:
            try:
                current_time = self.rtc.get_time().strftime("%d-%m-%Y %H:%M:%S")
                self.results["RTC"] = [True, current_time]
            except Exception:
                self.results["RTC"] = False

        self.print_results()

        # Stop SPS30
        if "airQuality" in self.sensor_instances:
            try:
                self.sensor_instances["airQuality"].stop()
            except:
                pass


if __name__ == "__main__":
    test_sensors = TestSensors()
    test_sensors.check_devices()

    while True:
        time.sleep(1000)

