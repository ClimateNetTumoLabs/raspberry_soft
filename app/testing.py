import time
from prettytable import PrettyTable
from sensors.bme280 import BME280Sensor
from sensors.ltr390 import LTR390Sensor
from sensors.sps30 import SPS30Sensor
from sensors.rain import RainSensor
from sensors.wind import WindSpeedSensor, WindDirectionSensor
from rtc import RTCControl
import warnings

# Ignore gpiozero warnings
warnings.filterwarnings("ignore", message="Falling back from lgpio", module="gpiozero.devices")
def check_sensor(name, sensor):
    """Return (status, data) tuple similar to previous TestSensors logic."""
    try:
        if name == "RTC":
            data = sensor.get_time()
            status = True if data else False
            return status, data.strftime("%Y-%m-%d %H:%M:%S") if status else None

        data = sensor.read_data()
        if data is None:
            return False, None

        # If data is a dict, check if any value is None
        if isinstance(data, dict):
            status = all(v is not None for v in data.values())
        else:
            status = True

        return status, data

    except Exception:
        return False, None


if __name__ == "__main__":
    # Initialize sensors
    sensors = {
        "RTC": RTCControl(),
        "BME280": BME280Sensor(),
        "LTR390": LTR390Sensor(),
        "SPS30": SPS30Sensor(),
        "Rain": RainSensor(),
        "Wind Speed": WindSpeedSensor(),
        "Wind Direction": WindDirectionSensor()
    }

    # Prepare table
    table = PrettyTable()
    table.field_names = ["Sensor", "Status", "Data"]

    for name, sensor in sensors.items():
        status, data = check_sensor(name, sensor)
        table.add_row([name, status, data])

    print(table)

    # Stop SPS30 if needed
    if hasattr(sensors.get("SPS30"), "stop"):
        sensors["SPS30"].stop()

