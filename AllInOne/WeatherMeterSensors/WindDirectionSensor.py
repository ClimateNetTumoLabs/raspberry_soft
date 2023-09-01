import json
import time
import math
import os
from gpiozero import MCP3008


class WindDirection():
    """
    A class representing a wind direction sensor that reads data from an analog sensor and calculates wind direction.

    Attributes:
        adc_channel (int): The ADC channel used to read analog data. Default is 0.
        config_file (str): The name of the JSON configuration file. Default is "directions_config.json".
        adc_max (int): The maximum ADC value. Default is 1024.
        adc_vref (float): The ADC reference voltage. Default is 5.12V.
        wind_interval (int): The time interval (in seconds) for collecting wind direction data. Default is 5.

    Methods:
        calculate_max_min_adc(): Calculates the ADC values corresponding to direction ranges.
        calculate_vout(ra, rb, vin): Calculates the output voltage based on resistor values and input voltage.
        get_dir(adc_value): Determines the wind direction angle based on the ADC value.
        get_direction_label(angle): Gets the label for the wind direction based on the angle.
        get_average(angles): Calculates the average wind direction angle from a list of angles.
        get_data(): Gets the wind direction label based on collected data.
        add_data(): Collects and processes wind direction data.
        reset(): Resets collected data.
    """

    def __init__(self, adc_channel=0, config_file="directions_config.json", adc_max=1024, adc_vref=5.12, wind_interval=5):
        """
        Initializes the WindDirection sensor with specified attributes and loads configuration data from a JSON file.

        Args:
            adc_channel (int, optional): The ADC channel used to read analog data. Defaults to 0.
            config_file (str, optional): The name of the JSON configuration file. Defaults to "directions_config.json".
            adc_max (int, optional): The maximum ADC value. Defaults to 1024.
            adc_vref (float, optional): The ADC reference voltage. Defaults to 5.12V.
            wind_interval (int, optional): The time interval (in seconds) for collecting wind direction data. Defaults to 5.
        """
        self.adc_channel = adc_channel
        self.config_file = config_file
        self.adc_max = adc_max
        self.adc_vref = adc_vref
        self.wind_interval = wind_interval

        self.data = []
        self.data_count = []

        self.adc = MCP3008(adc_channel)

        config_file_path = os.path.join(os.path.dirname(__file__), config_file)

        with open(config_file_path, "r") as f:
            self.config = json.load(f)

        vin = self.config["vin"]
        vdivider = self.config["vdivider"]

        for dir in self.config["directions"]:
            dir["vout"] = self.calculate_vout(vdivider, dir["ohms"], vin)
            dir["adc"] = round(self.adc_max * (dir["vout"] / self.adc_vref), 3)

        self.calculate_max_min_adc()

    def calculate_max_min_adc(self):
        """
        Calculates the ADC values corresponding to direction ranges.
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
        Calculates the output voltage based on resistor values and input voltage.

        Args:
            ra (float): Resistance value of resistor A.
            rb (float): Resistance value of resistor B.
            vin (float): Input voltage.

        Returns:
            float: Calculated output voltage.
        """
        return (float(rb) / float(ra + rb)) * float(vin)

    def get_dir(self, adc_value):
        """
        Determines the wind direction angle based on the ADC value.

        Args:
            adc_value (float): ADC value read from the sensor.

        Returns:
            float: Wind direction angle.
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
        Gets the label for the wind direction based on the angle.

        Args:
            angle (float): Wind direction angle.

        Returns:
            str: Wind direction label.
        """
        for dir in self.config["directions_labels"]:
            if angle >= dir["angle_min"] and angle < dir["angle_max"]:
                return dir["dir"]

    def get_average(self, angles):
        """
        Calculates the average wind direction angle from a list of angles.

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
        elif s < 0 and c > 0:
            average = arc + 360

        return 0.0 if average == 360 else average

    def get_data(self):
        """
        Gets the wind direction label based on collected data.

        Returns:
            str: Wind direction label.
        """
        if not self.data:
            return None
        
        angle = sum(self.data) / len(self.data)
        return angle
    
    def add_data(self):
        """
        Collects and processes wind direction data.
        """
        start_time = time.time()
        data = []

        while time.time() - start_time <= self.wind_interval:
            adc_value = self.adc.value * 1000
            direction = self.get_dir(adc_value)
            if direction is not None:
                data.append(direction)
        self.data.append(self.get_average(data))
    
    def reset(self):
        """
        Resets collected data.
        """
        self.data.clear()
