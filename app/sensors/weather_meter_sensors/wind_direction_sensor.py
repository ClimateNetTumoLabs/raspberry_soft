import json
import math
import os
import time
from time import sleep

from config import SENSORS
from gpiozero import MCP3008
from logger_config import logging


class WindDirection:
    """
    Class to handle wind direction sensing using an MCP3008 ADC.

    Attributes:
        adc_channel (int): ADC channel number.
        config_file (str): File path to JSON configuration file.
        adc_max (int): Maximum ADC value.
        adc_vref (float): Reference voltage for ADC.
        wind_interval (int): Time interval for reading wind direction.
        adc (gpiozero.MCP3008): MCP3008 ADC instance.
        working (bool): Flag indicating if the sensor is operational.
        config (dict): Configuration data loaded from JSON file.

    Methods:
        calculate_vout_adc: Calculates voltage output and ADC values for each direction based on calibration data.
        calculate_max_min_adc: Determines minimum and maximum ADC values for each direction.
        calculate_vout: Calculates voltage output based on resistor values and input voltage.
        get_dir: Determines wind direction based on ADC value.
        get_direction_label: Returns direction label based on angle.
        get_average: Computes average wind direction angle from a list of angles.
        read_data: Reads and returns the wind direction based on ADC readings within a specified interval.
    """

    def __init__(self) -> None:
        """
        Initializes the WindDirection sensor instance.
        """
        sensor_info = SENSORS["wind_direction"]
        self.adc_channel = sensor_info["adc_channel"]
        self.config_file = sensor_info["config_file"]
        self.adc_max = sensor_info["adc_max"]
        self.adc_vref = sensor_info["adc_vref"]
        self.wind_interval = sensor_info["reading_time"]
        self.adc = MCP3008(self.adc_channel)
        self.working = sensor_info["working"]

        config_file_path = os.path.join(os.path.dirname(__file__), self.config_file)
        with open(config_file_path, "r") as f:
            self.config = json.load(f)

        self.calculate_vout_adc()
        self.calculate_max_min_adc()

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
        Determines minimum and maximum ADC values for each direction.
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
        Calculates voltage output based on resistor values and input voltage.

        Args:
            ra (float): Resistor value Ra.
            rb (float): Resistor value Rb.
            vin (float): Input voltage.

        Returns:
            float: Calculated voltage output.
        """
        return (float(rb) / float(ra + rb)) * float(vin)

    def get_dir(self, adc_value) -> int:
        """
        Determines wind direction based on ADC value.

        Args:
            adc_value (int): ADC value from the sensor.

        Returns:
            int: Wind direction angle if found, None otherwise.
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

    def get_direction_label(self, angle: float) -> str:
        """
        Returns direction label based on angle.

        Args:
            angle (float): Wind direction angle.

        Returns:
            str: Direction label (e.g., "N", "NE", etc.).
        """
        for dir in self.config["directions_labels"]:
            if dir["angle_min"] <= angle < dir["angle_max"]:
                return dir["dir"]

    def get_average(self, angles) -> float:
        """
        Computes average wind direction angle from a list of angles.

        Args:
            angles (list): List of wind direction angles.

        Returns:
            float: Average wind direction angle.
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
        Reads and returns the wind direction based on ADC readings within a specified interval.

        Returns:
            str: Wind direction label (e.g., "N", "NE", etc.).
        """
        data = None

        if self.working:
            try:
                start_time = time.time()
                direction_data = []

                while time.time() - start_time <= self.wind_interval:
                    adc_value = self.adc.value * 1000
                    direction = self.get_dir(adc_value)
                    if direction is not None:
                        direction_data.append(direction)
                    sleep(1)

                average_direction = self.get_average(direction_data)
                data = self.get_direction_label(average_direction)
            except ZeroDivisionError as e:
                logging.error(f"ZeroDivision error occurred during reading WindDirection: {e}")
            except Exception as e:
                logging.error(f"Error occurred during reading data from WindDirection: {e}",
                              exc_info=True)

        return data
