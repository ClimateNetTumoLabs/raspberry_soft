import datetime
import time

import adafruit_ds3231
import board


class RTCControl:
    def __init__(self) -> None:
        """
        Initializes the RTCControl instance.
        """
        self.i2c = board.I2C()
        self.rtc = adafruit_ds3231.DS3231(self.i2c)

    def change_time(self, new_time: datetime.datetime) -> None:
        try:
            self.rtc.datetime = new_time.timetuple()
        except Exception as e:
            raise RuntimeError(f"Error while changing time: {e}")

    def get_time(self) -> datetime.datetime:
        try:
            rtc_datetime = time.mktime(self.rtc.datetime)
            return datetime.datetime.fromtimestamp(rtc_datetime)
        except Exception as e:
            raise RuntimeError(f"Error while getting time: {e}")