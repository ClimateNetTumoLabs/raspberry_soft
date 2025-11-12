from sensors.bme280 import BME280Sensor
from sensors.ltr390 import LTR390Sensor
from sensors.sps30 import SPS30Sensor
from sensors.rain import RainSensor
from sensors.wind import WindSpeedSensor, WindDirectionSensor
from prettytable import PrettyTable
from rtc import RTCControl
import warnings
import os

# Suppress gpiozero fallback warnings
warnings.filterwarnings("ignore", message="Falling back from lgpio", module="gpiozero.devices")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def read_all_sensors(sensors):
    table = PrettyTable()
    table.field_names = ["Time", "Sensor", "Connected", "Data"]

    now = RTCControl.get_time()

    for name, sensor_class in sensors.items():
        connected = False
        data = None

        try:
            sensor = sensor_class()
            # Check connection flag
            if hasattr(sensor, "connected"):
                connected = bool(sensor.connected)
            else:
                connected = True  # assume True if not defined

            data = sensor.read_data()
        except Exception as e:
            data = f"Error: {e}"
            connected = False

        table.add_row([now, name, connected, data])

    return table


if __name__ == "__main__":
    sensors = {
        "BME280 (Temp/Pressure/Humidity)": BME280Sensor,
        "LTR390 (UV/Lux)": LTR390Sensor,
        "SPS30 (Air Quality)": SPS30Sensor,
        "Rain Sensor": RainSensor,
        "Wind Speed": WindSpeedSensor,
        "Wind Direction": WindDirectionSensor,
    }

    while True:
        clear_screen()
        print("=== Sensor Testing Dashboard ===\n")
        table = read_all_sensors(sensors)
        print(table)
        print("\nPress [Enter] to refresh or type 'q' to quit.")
        user_input = input("> ").strip().lower()
        if user_input == "q":
            sensors["SPS30 (Air Quality)"].stop()
            print("Exiting...")
            break
