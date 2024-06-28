import json
import math
import os
import time
from time import sleep

from config import SENSORS
from gpiozero import MCP3008
from logger_config import logging


class WindDirection:
    def __init__(self) -> None:
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
        return (float(rb) / float(ra + rb)) * float(vin)

    def get_dir(self, adc_value) -> int:
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
        for dir in self.config["directions_labels"]:
            if dir["angle_min"] <= angle < dir["angle_max"]:
                return dir["dir"]

    def get_average(self, angles) -> float:
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
        data = None

        if self.working:
            try:
                start_time = time.time()
                data = []

                while time.time() - start_time <= self.wind_interval:
                    adc_value = self.adc.value * 1000
                    direction = self.get_dir(adc_value)
                    if direction is not None:
                        data.append(direction)
                    sleep(1)

                data = self.get_direction_label(self.get_average(data))
            except Exception as e:
                logging.error(f"Error occurred during reading data from WeatherDirection sensor: {str(e)}", exc_info=True)

        return data
