from adafruit_ltr390 import LTR390, Gain, Resolution, MeasurementDelay
import board
import busio
from config import SENSORS
import time


class LightSensor:
    """
    Interface for interacting with the LTR390 light sensor.
    """

    def __init__(self) -> None:
        """
        Initializes the LightSensor instance.
        """
        self.sensor = None
        self.i2c = None
        self.sensor_info = SENSORS["light_sensor"]
        self.working = self.sensor_info["working"]

        if self.working:
            self.setup_sensor()

    def setup_sensor(self) -> bool:
        """
        Sets up the LTR390 sensor instance.
        Returns:
            bool: True if sensor setup was successful, False otherwise.
        """
        for i in range(3):
            try:
                self.i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = LTR390(self.i2c)

                # Set resolution to 20-bit and gain to 3x (similar to the C++ example)
                self.sensor.resolution = Resolution.RESOLUTION_16BIT
                self.sensor.gain = Gain.GAIN_3X

                self.is_day_mode = False
                self.last_mode_check = 0
                self.MODE_CHECK_INTERVAL = 15  # Check every 15 seconds

                # Thresholds for switching modes (based on lux)
                self.DAY_THRESHOLD = 1000  # Switch to day mode above this
                self.NIGHT_THRESHOLD = 200  # Switch to night mode below this

                # Saturation detection
                self.MAX_20BIT = 1048575  # 2^20 - 1
                self.MAX_18BIT = 262143  # 2^18 - 1
                self.MAX_16BIT = 65535  # 2^16 - 1

                self.set_night_mode()

                break
            except Exception as e:
                print(f"Error occurred during creating object for LTR390 sensor: {e}")

        return self.sensor is not None

    def set_night_mode(self):
        """Configure for low light conditions - maximize sensitivity"""
        if not self.is_day_mode:
            return

        # Higher gain for sensitivity
        self.sensor.gain = Gain.GAIN_9X
        # Maximum resolution for precision
        self.sensor.resolution = Resolution.RESOLUTION_20BIT
        # Slower measurement for better accuracy
        self.sensor.measurement_delay = MeasurementDelay.DELAY_200MS

        self.is_day_mode = False
        time.sleep(0.2)  # Allow sensor to stabilize

    def set_day_mode(self):
        """Configure for direct sunlight - prevent saturation"""
        if self.is_day_mode:
            return

        # Use lowest gain to prevent saturation
        self.sensor.gain = Gain.GAIN_18X
        # Use 18-bit resolution for good precision without saturation
        self.sensor.resolution = Resolution.RESOLUTION_18BIT
        # Faster measurement for responsive readings
        self.sensor.measurement_delay = MeasurementDelay.DELAY_50MS

        self.is_day_mode = True
        time.sleep(0.1)  # Allow sensor to stabilize

    def is_saturated(self, raw_value):
        """Check if sensor is saturated based on current resolution"""
        current_res = self.sensor.resolution

        if current_res == Resolution.RESOLUTION_20BIT:
            return raw_value >= (self.MAX_20BIT * 0.95)  # 95% of max
        elif current_res == Resolution.RESOLUTION_18BIT:
            return raw_value >= (self.MAX_18BIT * 0.95)
        elif current_res == Resolution.RESOLUTION_16BIT:
            return raw_value >= (self.MAX_16BIT * 0.95)

        return False

    def auto_adjust_mode(self):
        """Automatically adjust sensor configuration based on conditions"""
        current_time = time.time()

        # Don't check too frequently
        if current_time - self.last_mode_check < self.MODE_CHECK_INTERVAL:
            return

        self.last_mode_check = current_time

        try:
            # Get current lux reading
            current_lux = self.sensor.lux

            # Also check for saturation
            raw_als = self.sensor.light
            is_saturated = self.is_saturated(raw_als)

            # Decision logic
            if is_saturated or (not self.is_day_mode and current_lux > self.DAY_THRESHOLD):
                self.set_day_mode()
            elif self.is_day_mode and current_lux < self.NIGHT_THRESHOLD:
                self.set_night_mode()

        except Exception as e:
            print(f"Error in auto-adjust: {e}")

    def get_accurate_uvi(self):
        """Calculate accurate UV Index using Adafruit's formula"""
        try:
            # The library's built-in UVI calculation is already accurate
            return self.sensor.uvi
        except Exception as e:
            print(f"Error reading UVI: {e}")
            return 0.0

    def get_accurate_lux(self):
        """Get accurate lux reading"""
        try:
            return self.sensor.lux
        except Exception as e:
            print(f"Error reading lux: {e}")
            return 0.0

    def read_data(self) -> dict:
        """
        Reads light data from the LTR390 sensor.
        Returns:
            dict: Dictionary containing light data (uv and lux).
        """
        data = {"uv": None, "lux": None}

        if self.working:
            if self.sensor is None:
                if not self.setup_sensor():
                    return data

            try:
                self.auto_adjust_mode()
                lux = self.get_accurate_lux()
                uvi = self.get_accurate_uvi()

            except AttributeError as e:
                print(f"Attribute error while reading LTR390: {e}")
            except OSError as e:
                print(f"OS error while reading LTR390: {e}")
            except Exception as e:
                print(f"Unhandled exception while reading LTR390: {e}", exc_info=True)
            else:
                data["uv"] = round(uvi)
                data["lux"] = lux

        return data