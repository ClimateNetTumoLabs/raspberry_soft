from ..base_sensor import BaseSensor
from gpiozero import MCP3008, Button
import math
import time


class WindSensor(BaseSensor):
    """Wind sensor measuring speed and direction."""

    def __init__(self, config_manager):
        super().__init__(config_manager, "wind_sensor")
        if not self.enabled:
            return

        cfg = self.config.get_sensor_config(self.name)

        # Configurable pins and parameters
        self.adc_channel_num = cfg.get("adc_channel", 0)
        self.pulse_pin_num = cfg.get("pulse_pin", 17)
        self.coefficient = cfg.get("speed_coefficient", 2.4)  # adjust if needed

        # Initialize hardware
        self.adc_channel = MCP3008(channel=self.adc_channel_num)
        self.pulse_pin = Button(self.pulse_pin_num)
        self.pulse_count = 0
        self.pulse_pin.when_pressed = self._count_pulse
        self.last_wind_check = time.time()

    def _count_pulse(self):
        """Increment pulse count for wind speed calculation."""
        self.pulse_count += 1

    def _read_sensor(self):
        """Read wind speed and direction."""
        if not self.enabled:
            return None

        now = time.time()
        elapsed = now - self.last_wind_check
        self.last_wind_check = now

        if elapsed == 0:
            return {"speed": 0, "direction": 0}

        # Wind speed calculation (pulses per second * calibration factor)
        rotations = self.pulse_count
        self.pulse_count = 0
        wind_speed = (rotations / elapsed) * self.coefficient

        # Wind direction
        voltage = self.adc_channel.value * 3.3
        direction_deg = self._convert_voltage_to_direction(voltage)

        return {
            "speed": wind_speed,
            "direction": direction_deg,
        }

    def _convert_voltage_to_direction(self, voltage):
        """Convert voltage from wind vane to direction in degrees."""
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
