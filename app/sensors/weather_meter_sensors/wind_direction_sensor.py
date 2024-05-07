import json
import time
import math
import os
from time import sleep
from gpiozero import MCP3008
from logger_config import logging
from config import SENSORS


class WindDirection:
    """
    Represents a wind direction sensor.

    This class reads wind direction data from an analog sensor connected to the MCP3008 ADC (Analog to Digital
    Converter). It calculates the average wind direction over a specified time interval and returns a direction label
    corresponding to the average angle.

    Args:
        adc_channel (int, optional): The ADC channel connected to the wind direction sensor. Defaults to 0.
        config_file (str, optional): Path to the JSON configuration file containing sensor calibration data.
            Defaults to "directions_config.json".
        adc_max (int, optional): Maximum ADC value. Defaults to 1024.
        adc_vref (float, optional): ADC reference voltage. Defaults to 5.12.
        testing (bool, optional): Flag indicating whether the sensor is in testing mode. Defaults to False.

    Attributes:
        adc_channel (int): The ADC channel connected to the wind direction sensor.
        config_file (str): Path to the JSON configuration file containing sensor calibration data.
        adc_max (int): Maximum ADC value.
        adc_vref (float): ADC reference voltage.
        wind_interval (float): Time interval for wind direction readings.
        adc (MCP3008): An instance of the MCP3008 class for ADC interfacing.
        config (dict): Configuration parameters loaded from the JSON config file.
        testing (bool): Flag indicating whether the sensor is in testing mode.

    Methods:
        calculate_vout_adc() -> None: Calculates voltage output and ADC values for each direction
        based on calibration data.
        calculate_max_min_adc() -> None: Calculates the minimum and maximum ADC values for each direction.
        calculate_vout(ra, rb, vin) -> float: Calculates voltage output based on voltage divider parameters.
        get_dir(adc_value) -> int: Determines the wind direction angle based on ADC value.
        get_direction_label(angle) -> str: Determines the wind direction label based on angle.
        get_average(angles) -> float: Calculates the average wind direction from a list of angles.
        read_data() -> str: Reads wind direction data from the sensor and returns the average direction label.
    """

    def __init__(self,
                 adc_channel=0,
                 config_file="directions_config.json",
                 adc_max=1024,
                 adc_vref=5.12,
                 testing=False) -> None:
        """
        Initializes the WindDirection object.

        Args:
            adc_channel (int, optional): The ADC channel connected to the wind direction sensor. Defaults to 0.
            config_file (str, optional): Path to the JSON configuration file containing sensor calibration data.
                Defaults to "directions_config.json".
            adc_max (int, optional): Maximum ADC value. Defaults to 1024.
            adc_vref (float, optional): ADC reference voltage. Defaults to 5.12.
            testing (bool, optional): Flag indicating whether the sensor is in testing mode. Defaults to False.
        """
        sensor_info = SENSORS["wind_direction"]
        self.adc_channel = adc_channel
        self.config_file = config_file
        self.adc_max = adc_max
        self.adc_vref = adc_vref
        self.wind_interval = sensor_info["reading_time"]
        self.adc = MCP3008(adc_channel)

        config_file_path = os.path.join(os.path.dirname(__file__), config_file)
        with open(config_file_path, "r") as f:
            self.config = json.load(f)

        self.calculate_vout_adc()
        self.calculate_max_min_adc()

        self.testing = testing

    def calculate_vout_adc(self) -> None:
        """
        Calculates voltage output and ADC values for each direction based on calibration data.
        """
        vin = self.config["vin"]
        vdivider = self.config["vdivider"]

        for dir in self.config["directions"]:
            dir["vout"] = self.calculate_vout(vdivider, dir["ohms"], vin)
            dir["adc"] = round(self.adc_max * (dir["vout"] / self.adc_vref), 3)

    def calculate_max_min_adc(self) -> None:
        """
        Calculates the minimum and maximum ADC values for each direction.
        """
        sorted_by_adc = sorted(self.config["directions"], key=lambda x: x["adc"])

        for index, dir in enumerate(sorted_by_adc):
            if index > 0:
                below = sorted_by_adc[index - 1]
                delta = (dir["adc"] - below["adc"]) / 2.0
                dir["adcmin"] = dir["adc"] - delta + 1
            else:
                dir["adcmin"] = 1

            if index < (len(sorted_by_adc) - 1):
                above = sorted_by_adc[index + 1]
                delta = (above["adc"] - dir["adc"]) / 2.0
                dir["adcmax"] = dir["adc"] + delta
            else:
                dir["adcmax"] = self.adc_max - 1

    def calculate_vout(self, ra, rb, vin) -> float:
        """
        Calculates voltage output based on voltage divider parameters.

        Args:
            ra (float): Resistance value of resistor A in the voltage divider circuit.
            rb (float): Resistance value of resistor B in the voltage divider circuit.
            vin (float): Input voltage to the voltage divider circuit.

        Returns:
            float: Calculated voltage output.
        """
        return (float(rb) / float(ra + rb)) * float(vin)

    def get_dir(self, adc_value) -> int:
        """
        Determines the wind direction angle based on ADC value.

        Args:
            adc_value (float): ADC value read from the sensor.

        Returns:
            int: Wind direction angle.
        """
        angle = None

        for dir in self.config["directions"]:
            if (
                    0 < adc_value <= dir["adcmax"] and
                    dir["adcmin"] <= adc_value < self.adc_max
            ):
                angle = dir["angle"]
                break

        return angle

    def get_direction_label(self, angle) -> str:
        """
        Determines the wind direction label based on angle.

        Args:
            angle (int): Wind direction angle.

        Returns:
            str: Wind direction label.
        """
        for dir in self.config["directions_labels"]:
            if dir["angle_min"] <= angle < dir["angle_max"]:
                return dir["dir"]

    def get_average(self, angles) -> float:
        """
        Calculates the average wind direction from a list of angles.

        Args:
            angles (list): List of wind direction angles.

        Returns:
            float: Average wind direction.
        """
        sin_sum = 0.0
        cos_sum = 0.0

        for angle in angles:
            r = math.radians(angle)
            sin_sum += math.sin(r)
            cos_sum += math.cos(r)

        flen = float(len(angles))
        s = sin_sum / flen
        c = cos_sum / flen
        arc = math.degrees(math.atan(s / c))
        average = 0.0

        if s > 0 and c > 0:
            average = arc
        elif c < 0:
            average = arc + 180
        elif s < 0 < c:
            average = arc + 360

        return 0.0 if average == 360 else average

    def read_data(self):
        """
        Reads wind direction data from the sensor and returns the average direction label.

        Returns:
            str: Average wind direction label.
        """
        try:
            start_time = time.time()
            data = []

            while time.time() - start_time <= (self.wind_interval if not self.testing else 3):
                adc_value = self.adc.value * 1000
                direction = self.get_dir(adc_value)
                if direction is not None:
                    data.append(direction)
                sleep(1)

            return self.get_direction_label(self.get_average(data))
        except Exception as e:
            logging.error(f"Error occurred during reading data from WeatherDirection sensor: {str(e)}", exc_info=True)
            return None
