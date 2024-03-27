import time
import board
import busio
from logger_config import *
from config import SENSORS
from Scripts.kalman import KalmanFilter
import adafruit_ltr390


class LightSensor:
    def __init__(self, testing=False) -> None:
        sensor_info = SENSORS["light_sensor"]
        self.working = sensor_info["working"]
        self.reading_time = sensor_info["reading_time"]
        self.testing = testing

        if self.working or self.testing:
            for i in range(3):
                try:
                    self.i2c = busio.I2C(board.SCL, board.SDA)
                    self.sensor = adafruit_ltr390.LTR390(self.i2c)
                    break
                except OSError or ValueError:
                    logging.error(
                        "Error occurred during creating object for LTR390 sensor: No I2C device at address")
                except Exception as e:
                    logging.error(f"Error occurred during creating object for LTR390 sensor: {str(e)}")

                if i == 2:
                    self.working = False

    def read_data(self) -> dict:
        if self.testing:
            pass

        if self.working:
            for i in range(3):
                uv_filter = KalmanFilter()
                lux_filter = KalmanFilter()

                data_uv = []
                data_lux = []

                start_time = time.time()

                try:
                    while time.time() - start_time <= self.reading_time:
                        uvi = self.sensor.uvi
                        lux = self.sensor.lux

                        data_uv.append(uv_filter.update(uvi))
                        data_lux.append(lux_filter.update(lux))

                        time.sleep(3)

                    uv_value = sum(data_uv[10:]) / len(data_uv[10:])
                    lux_value = sum(data_lux[10:]) / len(data_lux[10:])

                    return {
                        "uv": round(uv_value, 2),
                        "lux": round(lux_value, 2)
                    }
                except Exception as e:
                    logging.error(f"Error occurred during reading data from LTR390 sensor: {str(e)}", exc_info=True)

                    if i == 2:
                        return {
                            "uv": None,
                            "lux": None
                        }
        else:
            return {
                "uv": None,
                "lux": None
            }