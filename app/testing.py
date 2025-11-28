import os
import sys
from prettytable import PrettyTable
from sensors.read_sensors import sensors
from utils.rtc import RTCControl
from utils.network import check_internet
import warnings
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


warnings.filterwarnings("ignore", message="Falling back from lgpio", module="gpiozero.devices")


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
            # Auto-sync RTC if time difference is large
            self.sync_rtc_if_needed()
        except Exception as e:
            print(f"RTC initialization failed: {e}")
            self.rtc = None

        # start SPS30 only once
        if "airQuality" in self.sensor_instances:
            try:
                self.sensor_instances["airQuality"].start()
            except Exception as e:
                print("[SPS30] start() failed:", e)

    def sync_rtc_if_needed(self):
        """Sync RTC if time difference is too large"""
        if not self.rtc:
            return

        try:
            rtc_time = self.rtc.get_time()
            system_time = datetime.datetime.now()

            # Check if RTC time is reasonable (within 1 hour of system time)
            time_diff = abs((system_time - rtc_time).total_seconds())

            if time_diff > 3600:  # More than 1 hour difference
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
            "speed": [False],   # numeric wind speed
            "rain": [False],    # bool only
            "Network": False,
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

    def check_devices(self):
        self.reset_results()

        for name, instance in self.sensor_instances.items():
            # IMPORTANT: handle rain BEFORE calling instance.read_data()
            if name == "rain":
                try:
                    count = getattr(instance, "count", None)
                except Exception as e:
                    count = None
                    print(f"[rain] error reading count: {e}")

                # Debug print so you can see what's happening
                print(f"[rain debug] before read_data: count={count}")

                if isinstance(count, int) and count > 0:
                    self.results["rain"] = [True]
                else:
                    self.results["rain"] = [False]

                # call read_data() to let sensor clear its internal count as designed
                try:
                    instance.read_data()
                except Exception as e:
                    print(f"[rain] read_data() error: {e}")

                # continue to next sensor (we don't want to append read_data result to results)
                continue

            # speed: read numeric value normally
            if name == "speed":
                try:
                    res = instance.read_data()
                except Exception as e:
                    print(f"[speed] read_data() error: {e}")
                    self.results["speed"] = [False]
                    continue

                # Accept None as failure
                if res is None:
                    self.results["speed"] = [False]
                else:
                    self.results["speed"] = [True, res]
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
                # append for debugging / human readable
                self.results[name].append(res)
                if isinstance(res, dict) and any(v is None for v in res.values()):
                    self.results[name][0] = False

        # Network & RTC checks
        try:
            self.results["Network"] = check_internet()
        except Exception:
            self.results["Network"] = False

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
            # ENTER -> just loop again (sensors not reinitialized)
    except KeyboardInterrupt:
        tester.cleanup()
        start_main_service()
        print("\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()