from logger_config import logging
from gpiozero import Button, MCP3008
from config import SENSORS
import time

class WindSpeedSensor:
    """Wind Speed Sensor — counts pulses from an anemometer and converts to speed."""

    def __init__(self):
        conf = SENSORS["speed"]
        self.working = conf["working"]
        self.speed = Button(conf["pin"])
        self.speed.when_pressed = self._increment
        self.count = 0
        self.last_time = time.time()
        logging.info("[Wind speed] Initialized")

    def _increment(self):
        self.count += 1

    def read_data(self):
        """Return wind speed in m/s (None if disabled or error)."""
        data = {"speed": None}
        if self.working:
            try:
                now = time.time()
                elapsed = now - self.last_time
                # Capture count atomically
                current_count = self.count
                self.count = 0
                self.last_time = now

                # Calculate speed (example calibration factor)
                speed_kmh = (current_count / elapsed) * 2.4  # km/h
                speed_m_s = speed_kmh / 3.6  # convert to m/s
                data["speed"] = round(speed_m_s, 2)
            except Exception as e:
                logging.error(f"Error occured in WindSpeed: {e}")
        return data


class WindDirectionSensor:
    """Wind Direction Sensor — reads voltage from MCP3008 and returns 16-point compass direction."""

    def __init__(self):
        conf = SENSORS["direction"]
        self.working = conf["working"]
        self.adc = MCP3008(channel=conf["adc_channel"])
        self.adc_max = conf["adc_max"]  # MCP3008 is 10-bit (0-1023)
        self.vref = conf["adc_vref"]

        # Your calibrated voltages for 16 directions
        self.volts = {
            0.0: 3.84, 22.5: 1.98, 45.0: 2.25, 67.5: 0.41,
            90.0: 0.45, 112.5: 0.32, 135.0: 0.90, 157.5: 0.62,
            180.0: 1.40, 202.5: 1.19, 225.0: 3.08, 247.5: 2.93,
            270.0: 4.62, 292.5: 4.04, 315.0: 4.33, 337.5: 3.43
        }

        # Calculate ADC values from voltages
        self.directions = []
        for angle, voltage in self.volts.items():
            adc_value = (voltage / self.vref) * self.adc_max
            self.directions.append({
                "angle": angle,
                "voltage": voltage,
                "adc": adc_value
            })

        # Calculate dynamic min/max ranges
        self._calculate_adc_ranges()

        logging.info("[Wind direction] Initialized")

    def _calculate_adc_ranges(self):
        """Calculate adcmin and adcmax for each direction based on midpoints"""
        # Sort by ADC value
        sorted_dirs = sorted(self.directions, key=lambda x: x["adc"])

        for index, direction in enumerate(sorted_dirs):
            # Calculate minimum ADC value
            if index > 0:
                below = sorted_dirs[index - 1]
                delta = (direction["adc"] - below["adc"]) / 2.0
                direction["adcmin"] = direction["adc"] - delta
            else:
                direction["adcmin"] = 0

            # Calculate maximum ADC value
            if index < len(sorted_dirs) - 1:
                above = sorted_dirs[index + 1]
                delta = (above["adc"] - direction["adc"]) / 2.0
                direction["adcmax"] = direction["adc"] + delta
            else:
                direction["adcmax"] = self.adc_max

    def _get_angle_from_adc(self, adc_value):
        """Find angle based on ADC value using dynamic ranges"""
        for direction in self.directions:
            if direction["adcmin"] <= adc_value <= direction["adcmax"]:
                return direction["angle"]
        return None

    def _angle_to_direction(self, angle: float) -> str:
        """Convert angle (0–360) to 16-point compass direction"""
        directions = [
            "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
        ]
        ix = int((angle + 11.25) // 22.5) % 16
        return directions[ix]

    def read_data(self):
        """Take one wind direction reading and return compass direction."""
        data = {"direction": None}
        if self.working:
            try:
                # gpiozero 2.x returns normalized 0.0-1.0
                # Convert to raw ADC value (0-1023)
                normalized_value = self.adc.value
                raw_adc = normalized_value * self.adc_max
                voltage = normalized_value * self.vref

                # Find matching angle using dynamic ranges
                angle = self._get_angle_from_adc(raw_adc)

                if angle is not None:
                    direction = self._angle_to_direction(angle)
                    data["direction"] = direction
                else:
                    logging.warning(f"[Wind Dir] No match for ADC: {raw_adc:.1f} (V: {voltage:.2f}V)")

            except Exception as e:
                logging.error(f"Error in Wind direction: {e}", exc_info=True)
        return data
