import time
import board
import busio
from Scripts.kalman import KalmanFilter
from adafruit_si1145 import SI1145
from logger_config import *
from config import SENSORS


class LightSensor:
    def __init__(self, testing=False) -> None:
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
