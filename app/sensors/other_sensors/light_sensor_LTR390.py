import adafruit_ltr390
from adafruit_ltr390 import Gain,Resolution
import board
import busio
from config import SENSORS

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
                self.sensor = adafruit_ltr390.LTR390(self.i2c)

                # Set resolution to 20-bit and gain to 3x (similar to the C++ example)
                self.sensor.resolution = Resolution.RESOLUTION_16BIT
                self.sensor.gain = Gain.GAIN_3X

                # Set to UV mode (similar to setMode in the C++ code)
            

                break
            except Exception as e:
                print(f"Error occurred during creating object for LTR390 sensor: {e}")

        return self.sensor is not None

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
                # Get UV index and lux value (like in the C++ code where it reads raw UV data)
                uvi = self.sensor.uvi
                lux = self.sensor.lux
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
