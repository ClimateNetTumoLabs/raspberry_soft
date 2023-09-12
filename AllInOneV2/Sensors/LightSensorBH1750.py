import smbus2
import time
from logger_config import *


class LightSensor:
    def __init__(self, addr=0x23):
        self.POWER_DOWN = 0x00
        self.POWER_ON = 0x01
        self.RESET = 0x07

        self.bus = smbus2.SMBus(1)
        self.addr = addr
        self.power_down()
        self.set_sensitivity()
        self.ONE_TIME_HIGH_RES_MODE_2 = 0x21

    def _set_mode(self, mode):
        self.mode = mode
        self.bus.write_byte(self.addr, self.mode)

    def power_down(self):
        self._set_mode(self.POWER_DOWN)

    def power_on(self):
        self._set_mode(self.POWER_ON)

    def reset(self):
        self.power_on()
        self._set_mode(self.RESET)

    def oneshot_high_res2(self):
        self._set_mode(self.ONE_TIME_HIGH_RES_MODE_2)

    def set_sensitivity(self, sensitivity=150):
        if sensitivity < 31:
            self.mtreg = 31
        elif sensitivity > 254:
            self.mtreg = 254
        else:
            self.mtreg = sensitivity
        self.power_on()
        self._set_mode(0x40 | (self.mtreg >> 5))
        self._set_mode(0x60 | (self.mtreg & 0x1f))
        self.power_down()

    def get_result(self):
        data = self.bus.read_word_data(self.addr, self.mode)
        count = data >> 8 | (data & 0xff) << 8
        mode2coeff = 2 if (self.mode & 0x03) == 0x01 else 1
        ratio = 1 / (1.2 * (self.mtreg / 69.0) * mode2coeff)
        return ratio * count

    def wait_for_result(self, additional=0):
        basetime = 0.018 if (self.mode & 0x03) == 0x03 else 0.128
        time.sleep(basetime * (self.mtreg / 69.0) + additional)

    def read_data(self, additional_delay=0):
        for i in range(3):
            try:
                self.reset()
                self._set_mode(self.ONE_TIME_HIGH_RES_MODE_2)
                self.wait_for_result(additional=additional_delay)
                return self.get_result()
            except Exception as e:
                logging.error(f"Error occurred during reading data from Light sensor: {str(e)}", exc_info=True)
                if i == 2:
                    return None
