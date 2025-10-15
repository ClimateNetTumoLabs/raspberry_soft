from base_sensor import BaseSensor
from gpiozero import MCP3008, Button
import math
import time


class WindSensor(BaseSensor):
    def __init__(self, config_manager):
        super().__init__(config_manager, "wind_sensor")

        self.adc_channel = MCP3008(channel=0)  # wind direction
        self.pulse_pin = Button(17)  # wind speed reed switch
        self.pulse_count = 0
        self.pulse_pin.when_pressed = self._count_pulse
        self.last_wind_check = time.time()

    def _count_pulse(self):
        self.pulse_count += 1

    def _read_sensor(self):
        now = time.time()
        elapsed = now - self.last_wind_check
        self.last_wind_check = now

        # wind speed calculation (assuming 1 pulse per rotation)
        rotations = self.pulse_count
        self.pulse_count = 0
        wind_speed = (rotations / elapsed) * 2.4  # example coefficient in m/s

        # wind direction
        voltage = self.adc_channel.value * 3.3
        direction_deg = self._convert_voltage_to_direction(voltage)

        return {
            "wind_speed": wind_speed,
            "wind_direction": direction_deg,
        }

    def _convert_voltage_to_direction(self, voltage):
        # Example mapping (depends on your sensor)
        if voltage < 0.4:
            return 0
        elif voltage < 0.8:
            return 45
        elif voltage < 1.2:
            return 90
        elif voltage < 1.6:
            return 135
        elif voltage < 2.0:
            return 180
        elif voltage < 2.4:
            return 225
        elif voltage < 2.8:
            return 270
        else:
            return 315
