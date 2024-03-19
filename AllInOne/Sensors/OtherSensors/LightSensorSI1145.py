import time
import board
import busio
from Scripts.kalman import KalmanFilter
from adafruit_si1145 import SI1145
from logger_config import *
from config import SENSORS


class LightSensor:
    """
    Represents a light sensor for measuring visible, UV, and infrared light intensity.

    This class interacts with an SI1145 light sensor module via I2C interface to measure various aspects of light
    intensity including visible, UV, and infrared light.

    Args:
        testing (bool, optional): Specifies whether the sensor is in testing mode. Defaults to False.

    Attributes:
        working (bool): Indicates if the sensor is functioning properly.
        reading_time (int): Time duration for data reading in seconds.
        testing (bool): Specifies whether the sensor is in testing mode.
        i2c (busio.I2C): Instance of the I2C interface for communication with the sensor module.
        sensor (SI1145): Instance of the SI1145 light sensor module.

    Methods:
        test_read(): Reads data from the sensor in testing mode.
        read_data() -> dict: Reads data from the sensor and returns a dictionary of light intensity values.

    """

    def __init__(self, testing=False) -> None:
        """
        Initializes the LightSensor object.

        If the sensor is working or in testing mode, attempts to create an object for the light sensor module.
        Logs any errors encountered during the initialization process.

        Args:
            testing (bool, optional): Specifies whether the sensor is in testing mode. Defaults to False.
        """
        sensor_info = SENSORS["light_sensor"]
        self.working = sensor_info["working"]
        self.reading_time = sensor_info["reading_time"]
        self.testing = testing

        if self.working or testing:
            for i in range(3):
                try:
                    self.i2c = busio.I2C(board.SCL, board.SDA)
                    self.sensor = SI1145(self.i2c)
                    break
                except OSError or ValueError:
                    logging.error(
                        "Error occurred during creating object for Light sensor: No I2C device at address: 0x60")
                except Exception as e:
                    logging.error(f"Error occurred during creating object for Light sensor: {str(e)}")

                if i == 2:
                    self.working = False

    def test_read(self):
        """
        Reads data from the sensor in testing mode.

        Attempts to read visible, UV, and infrared light intensity values from the sensor.
        Logs any errors encountered during the reading process.

        Returns:
            dict: Dictionary containing light intensity values (visible, UV, infrared).
        """
        for i in range(3):
            try:
                vis, ir = self.sensor.als
                uv = self.sensor.uv_index

                return {
                    "light_vis": round(vis, 2),
                    "light_uv": round(uv, 2),
                    "light_ir": round(ir, 2)
                }
            except Exception as e:
                logging.error(f"Error occurred during reading data from Light sensor: {str(e)}", exc_info=True)

                if i == 2:
                    return {
                        "light_vis": None,
                        "light_uv": None,
                        "light_ir": None
                    }

    def read_data(self) -> dict:
        """
        Reads data from the sensor and returns a dictionary of light intensity values.

        If the sensor is in testing mode, invokes the test_read() method.
        If the sensor is working, attempts to filter and average light intensity values over a specified time duration.
        Logs any errors encountered during the reading process.

        Returns:
            dict: Dictionary containing light intensity values (visible, UV, infrared).
        """
        if self.testing:
            return self.test_read()
        if self.working:
            for i in range(3):
                vis_filter = KalmanFilter()
                uv_filter = KalmanFilter()
                ir_filter = KalmanFilter()

                data_vis = []
                data_uv = []
                data_ir = []

                start_time = time.time()

                try:
                    while time.time() - start_time <= self.reading_time:
                        vis, ir = self.sensor.als
                        uv = self.sensor.uv_index

                        data_vis.append(vis_filter.update(vis))
                        data_uv.append(uv_filter.update(uv))
                        data_ir.append(ir_filter.update(ir))

                        time.sleep(3)

                    vis_value = sum(data_vis[10:]) / len(data_vis[10:])
                    uv_value = sum(data_uv[10:]) / len(data_uv[10:])
                    ir_value = sum(data_ir[10:]) / len(data_ir[10:])

                    return {
                        "light_vis": round(vis_value, 2),
                        "light_uv": round(uv_value, 2),
                        "light_ir": round(ir_value, 2)
                    }
                except Exception as e:
                    logging.error(f"Error occurred during reading data from Light sensor: {str(e)}", exc_info=True)

                    if i == 2:
                        return {
                            "light_vis": None,
                            "light_uv": None,
                            "light_ir": None
                        }
        else:
            return {
                "light_vis": None,
                "light_uv": None,
                "light_ir": None
            }
