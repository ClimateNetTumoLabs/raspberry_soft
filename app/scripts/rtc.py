import datetime
import time

import adafruit_ds3231
import board


class RTCControl:
    """
    Provides control and interaction with a real-time clock (RTC) module.

    This class enables communication with a DS3231 RTC module via I2C interface to set and retrieve time.

    Attributes:
        i2c: Instance of the I2C interface for communication with the RTC module.
        rtc: Instance of the DS3231 RTC module.

    Methods:
        change_time(new_time): Changes the current time of the RTC module.
        get_time() -> datetime.datetime: Retrieves the current time from the RTC module.

    """

    def __init__(self):
        """
        Initializes the RTCControl object and establishes connection with the RTC module.
        """
        self.i2c = board.I2C()
        self.rtc = adafruit_ds3231.DS3231(self.i2c)

    def change_time(self, new_time: datetime.datetime):
        """
        Changes the current time of the RTC module.

        Args:
            new_time (datetime.datetime): New datetime object representing the desired time.

        Raises:
            RuntimeError: If an error occurs while changing the time.
        """
        try:
            self.rtc.datetime = new_time.timetuple()
        except Exception as e:
            raise RuntimeError(f"Error while changing time: {e}")

    def get_time(self) -> datetime.datetime:
        """
        Retrieves the current time from the RTC module.

        Returns:
            datetime.datetime: Current datetime object representing the time.

        Raises:
            RuntimeError: If an error occurs while getting the time.
        """
        try:
            rtc_datetime = time.mktime(self.rtc.datetime)
            return datetime.datetime.fromtimestamp(rtc_datetime)
        except Exception as e:
            raise RuntimeError(f"Error while getting time: {e}")
