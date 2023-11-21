import json
import time
import math
import os
from time import sleep
from gpiozero import MCP3008
from logger_config import *
from config import *


class WindDirection:
    """
    Class for reading wind direction from an analog sensor.

    This class provides methods to read wind direction data from an analog sensor connected to
    the MCP3008 ADC converter. It calculates wind direction based on ADC values and sensor
    configurations.

    Args:
        adc_channel (int): The ADC channel number to which the sensor is connected (default is 0).
        config_file (str): The JSON configuration file containing sensor calibration data (default is "directions_config.json").
        adc_max (int): Maximum ADC value (default is 1024).
        adc_vref (float): ADC reference voltage (default is 5.12).
        wind_interval (int): Time interval in seconds to collect wind direction data (default is 3).

    Attributes:
        adc_channel (int): The ADC channel number.
        config_file (str): The path to the configuration JSON file.
        adc_max (int): Maximum ADC value.
        adc_vref (float): ADC reference voltage.
        wind_interval (int): Time interval for collecting data.
        adc (MCP3008): An MCP3008 object for ADC communication.
        config (dict): Sensor configuration data.

    Methods:
        calculate_vout_adc(self):
            Calculate Vout and ADC values for each wind direction based on sensor configurations.

        calculate_max_min_adc(self):
            Calculate the minimum and maximum ADC values for each wind direction.

        calculate_vout(self, ra, rb, vin):
            Calculate Vout using resistor values and input voltage.

        get_dir(self, adc_value):
            Get the wind direction angle for a given ADC value.

        get_direction_label(self, angle):
            Get the wind direction label based on the angle.

        get_average(self, angles):
            Calculate the average wind direction from a list of angles.

        read_data(self):
            Read wind direction data from the sensor and return the direction label.

    """

    def __init__(self, adc_channel=0, config_file="directions_config.json", adc_max=1024, adc_vref=5.12):
        """
        Initialize the WindDirection class.

        This method initializes the WindDirection class and sets up the necessary attributes, such as ADC channel,
        configuration file, ADC parameters, and the ADC interface.

        Args:
            adc_channel (int): The ADC channel number to which the sensor is connected (default is 0).
            config_file (str): The JSON configuration file containing sensor calibration data (default is "directions_config.json").
            adc_max (int): Maximum ADC value (default is 1024).
            adc_vref (float): ADC reference voltage (default is 5.12).
            wind_interval (int): Time interval in seconds to collect wind direction data (default is 3).

        Attributes:
            adc_channel (int): The ADC channel number.
            config_file (str): The path to the configuration JSON file.
            adc_max (int): Maximum ADC value.
            adc_vref (float): ADC reference voltage.
            wind_interval (int): Time interval for collecting data.
            adc (MCP3008): An MCP3008 object for ADC communication.
            config (dict): Sensor configuration data.

        Returns:
            None
        """
        self.adc_channel = adc_channel
        self.config_file = config_file
        self.adc_max = adc_max
        self.adc_vref = adc_vref
        self.wind_interval = WIND_DIRECTION_READING_TIME
        self.adc = MCP3008(adc_channel)

        config_file_path = os.path.join(os.path.dirname(__file__), config_file)
        with open(config_file_path, "r") as f:
            self.config = json.load(f)

        self.calculate_vout_adc()
        self.calculate_max_min_adc()

    def calculate_vout_adc(self):
        """
        Calculate Vout and ADC values for each wind direction based on sensor configurations.

        This method calculates the Vout and ADC values for each wind direction specified in the
        sensor configuration. The results are stored in the `config` attribute.

        Returns:
            None
        """ 
        vin = self.config["vin"]
        vdivider = self.config["vdivider"]

        for dir in self.config["directions"]:
            dir["vout"] = self.calculate_vout(vdivider, dir["ohms"], vin)
            dir["adc"] = round(self.adc_max * (dir["vout"] / self.adc_vref), 3)
    
    def calculate_max_min_adc(self):
        """
        Calculate the minimum and maximum ADC values for each wind direction.

        This method sorts the wind directions by ADC values and calculates the minimum (adcmin)
        and maximum (adcmax) ADC values for each direction. The results are stored in the `config`
        attribute.

        Returns:
            None
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

    def calculate_vout(self, ra, rb, vin):
        """
        Calculate Vout using resistor values and input voltage.

        Args:
            ra (float): The value of resistor 'a' in the voltage divider circuit.
            rb (float): The value of resistor 'b' in the voltage divider circuit.
            vin (float): The input voltage.

        Returns:
            float: The calculated Vout voltage.
        """
        return (float(rb) / float(ra + rb)) * float(vin)

    def get_dir(self, adc_value):
        """
        Get the wind direction angle for a given ADC value.

        Args:
            adc_value (float): The ADC value to be converted to a wind direction angle.

        Returns:
            float or None: The wind direction angle in degrees, or None if no valid direction is found.
        """
        angle = None

        for dir in self.config["directions"]:
            if (
                adc_value > 0 and
                adc_value >= dir["adcmin"] and
                adc_value <= dir["adcmax"] and
                adc_value < self.adc_max
            ):
                angle = dir["angle"]
                break

        return angle
    
    def get_direction_label(self, angle):
        """
        Get the wind direction label based on the angle.

        Args:
            angle (float): The wind direction angle in degrees.

        Returns:
            str: The label representing the wind direction.
        """
        for dir in self.config["directions_labels"]:
            if angle >= dir["angle_min"] and angle < dir["angle_max"]:
                return dir["dir"]

    def get_average(self, angles):
        """
        Calculate the average wind direction from a list of angles.

        This method calculates the average wind direction angle from a list of angles using trigonometric
        functions. The result is an angle in degrees.

        Args:
            angles (list of float): List of wind direction angles in degrees.

        Returns:
            float: The average wind direction angle in degrees.
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
        elif s < 0 and c > 0:
            average = arc + 360

        return 0.0 if average == 360 else average

    def read_data(self):
        """
        Read wind direction data from the sensor and return the direction label.

        This method reads wind direction data from the sensor over a specified time interval and returns
        the label representing the average wind direction.

        Returns:
            str or None: The label representing the average wind direction, or None in case of an error.
        """
        try:
            start_time = time.time()
            data = []

            while time.time() - start_time <= self.wind_interval:
                adc_value = self.adc.value * 1000
                direction = self.get_dir(adc_value)
                if direction is not None:
                    data.append(direction)
                sleep(1)

            return self.get_direction_label(self.get_average(data))
        except Exception as e:
            logging.error(f"Error occurred during reading data from WeatherDirection sensor: {str(e)}", exc_info=True)
            return None
