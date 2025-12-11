import os
import sys
from prettytable import PrettyTable
from sensors.read_sensors import sensors
from utils.rtc import RTCControl
from utils.network import check_internet
import subprocess
import datetime

SERVICE_NAME = "ProgramAutoRun.service"

def stop_main_service():
    try:
        subprocess.run(["sudo", "systemctl", "stop", SERVICE_NAME], check=False)
        print(f"Stopped {SERVICE_NAME}")
    except Exception as e:
        print(f"Failed to stop {SERVICE_NAME}: {e}")

def start_main_service():
    try:
        subprocess.run(["sudo", "systemctl", "restart", SERVICE_NAME], check=False)
        print(f"Restarted {SERVICE_NAME}")
    except Exception as e:
        print(f"Failed to restart {SERVICE_NAME}: {e}")

class TestSensors:
    def __init__(self):
        self.init_once()
        self.reset_results()

    def init_once(self):
        os.system("clear")
        print("Initializing sensors (once)...")
        self.sensor_instances = {}
        for name, cls in sensors.items():
            try:
                self.sensor_instances[name] = cls()
            except Exception as e:
                print(f"Failed to init {name}: {e}")

        try:
            self.rtc = RTCControl()
            self.sync_rtc_if_needed()
        except Exception as e:
            print(f"RTC initialization failed: {e}")
            self.rtc = None

        # Start SPS30 only once
        if "airQuality" in self.sensor_instances:
            try:
                self.sensor_instances["airQuality"].start()
            except Exception as e:
                print("[SPS30] start() failed:", e)

        # Set up callbacks for pulse sensors
        if "speed" in self.sensor_instances:
            instance = self.sensor_instances["speed"]
            if hasattr(instance, 'speed'):
                instance.speed.when_pressed = self.speed_ok

        if "rain" in self.sensor_instances:
            instance = self.sensor_instances["rain"]
            if hasattr(instance, 'rain'):
                instance.rain.when_pressed = self.rain_ok

    def sync_rtc_if_needed(self):
        """Sync RTC if time difference is too large"""
        if not self.rtc:
            return

        try:
            rtc_time = self.rtc.get_time()
            system_time = datetime.datetime.now()
            time_diff = abs((system_time - rtc_time).total_seconds())

            if time_diff > 3600:
                print(f"RTC time differs by {time_diff} seconds. Syncing...")
                self.rtc.change_time(system_time)
                print("RTC synced with system time")
            else:
                print(f"RTC time is correct (diff: {time_diff}s)")
        except Exception as e:
            print(f"RTC sync check failed: {e}")

    def reset_results(self):
        self.results = {
            "tph": [True],
            "light": [True],
            "airQuality": [True],
            "direction": [True],
            "speed": [False],
            "rain": [False],
            "network": False,
            "RTC": False
        }

    def format_result(self, v):
        if isinstance(v, list):
            if len(v) > 1:
                ok, data = v
                if isinstance(data, dict):
                    data = "\n".join(f"{k}: {v}" for k, v in data.items())
                return f"{ok}\n\n{data}"
            return v[0]
        return v

    def print_results(self):
        os.system("clear")
        table = PrettyTable()
        table.field_names = ["Sensor", "Value"]
        for key, value in self.results.items():
            table.add_row([key, self.format_result(value)], divider=True)
        table.align = "l"
        print(table)
        print("\nPress ENTER to restart | press 'q' then ENTER to quit")

    def speed_ok(self):
        """Callback when wind speed sensor triggers"""
        if not self.results["speed"][0]:
            self.results["speed"] = [True]
            self.print_results()

    def rain_ok(self):
        """Callback when rain sensor triggers"""
        if not self.results["rain"][0]:
            self.results["rain"] = [True]
            self.print_results()

    def check_devices(self):
        self.reset_results()

        for name, instance in self.sensor_instances.items():
            # Rain sensor - just check if callback has triggered
            if name == "rain":
                # Callback already set self.results["rain"] if triggered
                continue

            # Speed sensor - read numeric value
            if name == "speed":
                try:
                    res = instance.read_data()
                    # If callback was triggered, show True with data
                    if self.results["speed"][0]:
                        if res is not None:
                            self.results["speed"] = [True]
                    # Otherwise stays False
                except Exception as e:
                    print(f"[speed] error: {e}")
                continue

            # general sensors
            try:
                res = instance.read_data()
            except Exception as e:
                print(f"[{name}] read_data() error: {e}")
                self.results[name][0] = False
                continue

            if res is None:
                self.results[name][0] = False
            else:
                self.results[name].append(res)
                if isinstance(res, dict) and any(v is None for v in res.values()):
                    self.results[name][0] = False

        # Network & RTC checks
        try:
            self.results["network"] = check_internet()
        except Exception:
            self.results["network"] = False

        if self.rtc:
            try:
                t = self.rtc.get_time().strftime("%d-%m-%Y %H:%M:%S")
                self.results["RTC"] = [True, t]
            except Exception:
                self.results["RTC"] = False

        self.print_results()

    def cleanup(self):
        if "airQuality" in self.sensor_instances:
            try:
                self.sensor_instances["airQuality"].stop()
            except Exception as e:
                print("[SPS30] stop() error:", e)


def main():
    stop_main_service()
    tester = TestSensors()
    try:
        while True:
            tester.check_devices()
            user_input = input().strip().lower()
            if user_input == "q":
                tester.cleanup()
                start_main_service()
                print("Exiting...")
                sys.exit(0)
    except KeyboardInterrupt:
        tester.cleanup()
        start_main_service()
        print("\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()