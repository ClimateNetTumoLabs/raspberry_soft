import os
from sensors.bme280 import BME280Sensor
from sensors.ltr390 import LTR390Sensor
from sensors.sps30 import SPS30Sensor
from sensors.rain import RainSensor
from sensors.wind import WindSpeedSensor, WindDirectionSensor
from rtc import RTCControl
import gpiozero.devices
import warnings
from prettytable import PrettyTable

# Ignore gpiozero warnings
warnings.filterwarnings("ignore", message="Falling back from lgpio", module="gpiozero.devices")

def get_status(sensor):
    """Return 'Connected' if sensor is connected, else 'Disconnected'."""
    return "Connected" if getattr(sensor, "connected", True) or getattr(sensor, "enabled", True) else "Disconnected"

def get_data(name, sensor):
    """Safely read sensor data, return 'Error' if something goes wrong."""
    try:
        if isinstance(sensor, RTCControl) or name == "RTC":
            return sensor.get_time()
        else:
            return sensor.read_data()
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    # Initialize sensors
    os.system("clear")
    sensors = {
        "RTC": RTCControl(),
        "BME280": BME280Sensor(),
        "LTR390": LTR390Sensor(),
        "Rain": RainSensor(),
        "Wind Speed": WindSpeedSensor(),
        "Wind Direction": WindDirectionSensor(),
        "SPS30": SPS30Sensor()
    }

    # Create table
    table = PrettyTable()
    table.field_names = ["Sensor", "Status", "Data"]

    for name, sensor in sensors.items():
        status = get_status(sensor)
        data = get_data(name, sensor)
        table.add_row([name, status, data])

    print(table)

    # Stop SPS30 if needed
    if hasattr(sensors["SPS30"], "stop"):
        sensors["SPS30"].stop()
