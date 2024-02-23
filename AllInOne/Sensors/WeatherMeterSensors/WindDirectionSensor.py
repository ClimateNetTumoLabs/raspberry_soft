"""
    Module for interacting with a wind direction sensor.

    This module provides a WindDirection class for reading wind direction data.

    Class Docstring:
    ----------------
    WindDirection:
        Interacts with a wind direction sensor to read wind direction data.

    Constructor:
        Initializes a WindDirection object based on the configuration specified in the SENSORS module.

    Class Attributes:
        adc_channel (int): ADC channel for the wind direction sensor.
        config_file (str): File name for the configuration file containing information about directions.
        adc_max (int): Maximum ADC value.
        adc_vref (float): ADC reference voltage.
        wind_interval (float): Time interval for collecting wind direction data.
        adc (MCP3008): An instance of the MCP3008 class from the gpiozero library for ADC input.
        config (dict): Wind direction configuration loaded from the config_file.

    Methods:
        calculate_vout_adc(self): Calculate Vout and ADC values for each wind direction based on the configuration.
        calculate_max_min_adc(self): Calculate the min and max ADC values for each wind direction.
        calculate_vout(self, ra, rb, vin): Calculate Vout based on resistor values and input voltage.
        get_dir(self, adc_value): Get wind direction based on ADC value.
        get_direction_label(self, angle): Get the direction label based on the angle.
        get_average(self, angles): Calculate the average wind direction from a list of angles.
        read_data(self): Read wind direction data over a specified time interval.

    Module Usage:
    -------------
    To use this module, create an instance of the WindDirection class. Call read_data() to get the average wind direction over the specified time interval.
"""

import json
import time
import math
import os
from time import sleep
from gpiozero import MCP3008
from logger_config import *
from config import SENSORS


class WindDirection:
    """
    Interacts with a wind direction sensor to read wind direction data.

    Attributes:
        adc_channel (int): ADC channel for the wind direction sensor.
        config_file (str): File name for the configuration file containing information about directions.
        adc_max (int): Maximum ADC value.
        adc_vref (float): ADC reference voltage.
        wind_interval (float): Time interval for collecting wind direction data.
        adc (MCP3008): An instance of the MCP3008 class from the gpiozero library for ADC input.
        config (dict): Wind direction configuration loaded from the config_file.
    """

    def __init__(self, adc_channel=0, config_file="directions_config.json", adc_max=1024, adc_vref=5.12, testing=False) -> None:
        """
        Initializes a WindDirection object based on the configuration specified in the SENSORS module.
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
        Calculate Vout and ADC values for each wind direction based on the configuration.
        """
        vin = self.config["vin"]
        vdivider = self.config["vdivider"]

        for dir in self.config["directions"]:
            dir["vout"] = self.calculate_vout(vdivider, dir["ohms"], vin)
            dir["adc"] = round(self.adc_max * (dir["vout"] / self.adc_vref), 3)

    def calculate_max_min_adc(self) -> None:
        """
        Calculate the min and max ADC values for each wind direction.
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
        Calculate Vout based on resistor values and input voltage.

        Parameters:
            ra (float): Resistor Ra value.
            rb (float): Resistor Rb value.
            vin (float): Input voltage.

        Returns:
            float: Vout value.
        """
        return (float(rb) / float(ra + rb)) * float(vin)

    def get_dir(self, adc_value) -> int:
        """
        Get wind direction based on ADC value.

        Parameters:
            adc_value (float): ADC value.

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
        Get the direction label based on the angle.

        Parameters:
            angle (float): Wind direction angle.

        Returns:
            str: Direction label.
        """
        for dir in self.config["directions_labels"]:
            if dir["angle_min"] <= angle < dir["angle_max"]:
                return dir["dir"]

    def get_average(self, angles) -> float:
        """
        Calculate the average wind direction from a list of angles.

        Parameters:
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
        Read wind direction data over a specified time interval.

        Returns:
            str: Direction label for the average wind direction.
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
