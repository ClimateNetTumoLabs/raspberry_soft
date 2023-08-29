import smbus2
import bme280
from time import sleep
import math


# Initialize and configure the BME280 sensor
port = 1
address = 0x76
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)


def get_altitude(p, t):
    """
    Function to calculate altitude above sea level based on atmospheric pressure and temperature.

    Args:
        p (float): Atmospheric pressure in hectopascals.
        t (float): Temperature in degrees Celsius.

    Returns:
        float: Altitude above sea level in meters.
    """
    p0 = 1013.25

    # Formula to calculate altitude based on atmospheric pressure and temperature
    h = 44330 * (1 - math.pow(p / p0, (1 / 5.255)))

    return round(h, 2)


try:
    while True:
        # Get data from the BME280 sensor
        data = bme280.sample(bus, address, calibration_params)

        # Print the measured values of temperature, pressure, humidity, and altitude
        print(f"Temperature: {round(data.temperature, 2)}\n"
              f"Pressure: {round(data.pressure, 2)}\n"
              f"Humidity: {round(data.humidity, 2)}\n"
              f"Altitude: {get_altitude(data.pressure, data.temperature)}")

        print("#" * 50)
        print()
        sleep(2)
except KeyboardInterrupt:
    # Handle the Ctrl+C keyboard interrupt gracefully
    print("Goodbye!")

