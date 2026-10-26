"""
Service mode for lab tests: live readings every READING_TIME seconds, without
waiting for the transmission. Readings are printed here only - nothing is sent
over MQTT or written to the local buffer.

Run on the station:

    cd app && venv/bin/python3 service_mode.py

ProgramAutoRun is stopped while this runs, because both need the same GPIO
pins and UART, and started again on exit (Ctrl+C).
"""

import datetime
import subprocess
import time

from metro_config import READING_TIME
from utils.sensor_manager import SensorManager
from version import SOFTWARE_NAME, __version__, metro_checksum

SERVICE_NAME = "ProgramAutoRun.service"


def main():
    subprocess.run(["sudo", "systemctl", "stop", SERVICE_NAME], check=False)
    print(f"{SOFTWARE_NAME} v{__version__}, SHA-256 {metro_checksum()}")
    print(f"Service mode: one reading every {READING_TIME}s. Nothing is sent or stored. Ctrl+C to stop.")

    sensor_manager = None
    try:
        # Same code path as the station, so the lab tests what is approved.
        sensor_manager = SensorManager()
        sensor_manager.start_sensors()  # includes the SPS30 warmup
        if sensor_manager.sps30() and not sensor_manager.sps30_started:
            print("SPS30 not started: outside its limits or failed to start (see parsing.log). PM shows as None.")

        # Discarded: wind speed and rain count since init, and the first
        # interval would include the warmup.
        sensor_manager.collect_single_reading()
        sensor_manager.get_rain_data()

        next_reading = time.monotonic() + READING_TIME
        while True:
            time.sleep(max(0.0, next_reading - time.monotonic()))
            next_reading += READING_TIME

            sensor_manager.measurement_buffer.clear()
            sensor_manager.collect_single_reading()
            # calculate_averages(), not get_averaged_data(): the direction is shown
            # even at zero wind speed, so the vane can be tested on a rotating table.
            data = sensor_manager.calculate_averages()
            data["rain"] = sensor_manager.get_rain_data()  # mm in the last interval
            sensor_manager.apply_pm_limits(data)  # same rule as the station applies

            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(now, "  ".join(f"{key}={value}" for key, value in data.items()), flush=True)

    except KeyboardInterrupt:
        print("\nStopping service mode")
    finally:
        if sensor_manager:
            sensor_manager.cleanup()
        subprocess.run(["sudo", "systemctl", "start", SERVICE_NAME], check=False)
        print(f"Started {SERVICE_NAME} again")


if __name__ == "__main__":
    main()
