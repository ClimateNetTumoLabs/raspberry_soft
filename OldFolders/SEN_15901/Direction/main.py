import json
import time
import math
import os
from gpiozero import MCP3008


class WindDirection():
    """
    A class representing a wind direction sensor.

    Attributes:
        adc_channel (int): The ADC channel number connected to the wind direction sensor.
        config_file (str): The path to the JSON configuration file containing direction data.
        adc_max (int): The maximum ADC value. Default is 1024.
        adc_vref (float): The ADC reference voltage. Default is 5.12 volts.
        wind_interval (int): The time interval (in seconds) for measuring wind direction.

    Methods:
        calculate_max_min_adc(): Calculates the ADC range (min and max) for each direction.
        calculate_vout(ra, rb, vin): Calculates the voltage across a voltage divider circuit.
        get_dir(adc_value): Determines the wind direction based on the ADC value.
        get_direction_label(angle): Returns the direction label for a given angle.
        get_average(angles): Calculates the average wind direction from a list of angles.
        get_data(): Gets wind direction data by measuring the wind direction for the specified wind interval.
    """

    def __init__(self, adc_channel=0, config_file="directions_config.json", adc_max=1024, adc_vref=5.12, wind_interval=3):
        """
        Initializes the WindDirection with the specified ADC channel, configuration file, and other parameters.

        Args:
            adc_channel (int, optional): The ADC channel number connected to the wind direction sensor.
                                        Defaults to 0.
            config_file (str, optional): The path to the JSON configuration file containing direction data.
                                         Defaults to "directions_config.json".
            adc_max (int, optional): The maximum ADC value. Defaults to 1024.
            adc_vref (float, optional): The ADC reference voltage. Defaults to 5.12 volts.
            wind_interval (int, optional): The time interval (in seconds) for measuring wind direction.
                                           Defaults to 3.
        """
        self.adc_channel = adc_channel
        self.config_file = config_file
        self.adc_max = adc_max
        self.adc_vref = adc_vref
        self.wind_interval = wind_interval

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
        Calculates the ADC range (min and max) for each direction based on the sorted ADC values.
        The calculated ranges are stored in the 'adcmin' and 'adcmax' keys of the direction dictionary.
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
        Calculates the voltage across a voltage divider circuit.

        Args:
            ra (float): The resistance of the first resistor in the voltage divider circuit.
            rb (float): The resistance of the second resistor in the voltage divider circuit.
            vin (float): The input voltage to the voltage divider circuit.

        Returns:
            float: The output voltage (Vout) across the voltage divider circuit.
        """
        return (float(rb) / float(ra + rb)) * float(vin)

    def get_dir(self, adc_value):
        """
        Determines the wind direction based on the ADC value.

        Args:
            adc_value (float): The ADC value obtained from the wind direction sensor.

        Returns:
            float or None: The wind direction angle in degrees (0 to 360) if a valid direction is found,
                           otherwise returns None.
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
        Returns the direction label for a given angle.

        Args:
            angle (float): The wind direction angle in degrees (0 to 360).

        Returns:
            str: The direction label corresponding to the given angle.
        """
        for dir in self.config["directions_labels"]:
            if angle >= dir["angle_min"] and angle < dir["angle_max"]:
                return dir["dir"]

    def get_average(self, angles):
        """
        Calculates the average wind direction from a list of angles.

        Args:
            angles (list): A list of wind direction angles in degrees (0 to 360).

        Returns:
            float: The average wind direction in degrees (0 to 360).
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
        Gets wind direction data by measuring the wind direction for the specified wind interval.

        Returns:
            str: The wind direction label.
        """
        data = []
        print("Measuring wind direction for %d seconds..." % self.wind_interval)
        start_time = time.time()

        while time.time() - start_time <= self.wind_interval:
            adc_value = self.adc.value * 1000
            direction = self.get_dir(adc_value)
            if direction is not None:
                data.append(direction)

        return self.get_direction_label(self.get_average(data))


if __name__ == "__main__":
    obj = WindDirection()
    while True:
        print(obj.get_data())
