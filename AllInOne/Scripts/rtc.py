import time
import board
import adafruit_ds3231
import datetime

class RTCControl:
    def __init__(self):
        """
        Class for controlling the DS3231 RTC module.
        """
        self.i2c = board.I2C()
        self.rtc = adafruit_ds3231.DS3231(self.i2c)

    def change_time(self, new_time: datetime.datetime):
        """
        Method for changing the time on the RTC module.

        :param new_time: New time in the format datetime.datetime.
        """
        try:
            self.rtc.datetime = new_time.timetuple()
        except Exception as e:
            raise RuntimeError(f"Error while changing time: {e}")

    def get_time(self) -> datetime.datetime:
        """
        Method for getting the current time from the RTC module.

        :return: Current time in the format datetime.datetime.
        """
        try:
            rtc_datetime = time.mktime(self.rtc.datetime)
            return datetime.datetime.fromtimestamp(rtc_datetime)
        except Exception as e:
            raise RuntimeError(f"Error while getting time: {e}")
