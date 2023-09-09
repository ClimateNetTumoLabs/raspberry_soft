import json
import time
import math
import os
from gpiozero import MCP3008


class WindDirection():
    def __init__(self, adc_channel=0, config_file="directions_config.json", adc_max=1024, adc_vref=5.12, wind_interval=5):
        self.adc_channel = adc_channel
        self.config_file = config_file
        self.adc_max = adc_max
        self.adc_vref = adc_vref
        self.wind_interval = wind_interval
        self.adc = MCP3008(adc_channel)

        config_file_path = os.path.join(os.path.dirname(__file__), config_file)
        with open(config_file_path, "r") as f:
            self.config = json.load(f)

        self.calculate_vout_adc()
        self.calculate_max_min_adc()

        self.data = []

    def calculate_vout_adc(self):
        vin = self.config["vin"]
        vdivider = self.config["vdivider"]

        for dir in self.config["directions"]:
            dir["vout"] = self.calculate_vout(vdivider, dir["ohms"], vin)
            dir["adc"] = round(self.adc_max * (dir["vout"] / self.adc_vref), 3)
    
    def calculate_max_min_adc(self):
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
        return (float(rb) / float(ra + rb)) * float(vin)

    def get_dir(self, adc_value):
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
        for dir in self.config["directions_labels"]:
            if angle >= dir["angle_min"] and angle < dir["angle_max"]:
                return dir["dir"]

    def get_average(self, angles):
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
        if not self.data:
            return None
        
        angle = sum(self.data) / len(self.data)
        return angle
    
    def add_data(self):
        start_time = time.time()
        data = []

        while time.time() - start_time <= self.wind_interval:
            adc_value = self.adc.value * 1000
            direction = self.get_dir(adc_value)
            if direction is not None:
                data.append(direction)

        self.data.append(self.get_average(data))
    
    def reset(self):
        self.data.clear()
