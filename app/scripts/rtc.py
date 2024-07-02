import datetime
import time

import adafruit_ds3231
import board


class RTCControl:
    """
    Controls a DS3231 Real-Time Clock (RTC) module.

    Attributes:
        i2c (board.I2C): The I2C bus used to communicate with the RTC.
        rtc (adafruit_ds3231.DS3231): The DS3231 RTC object.
    """

    def __init__(self) -> None:
        """
        Initializes the RTCControl instance.
        """
        self.i2c = board.I2C()
        self.rtc = adafruit_ds3231.DS3231(self.i2c)

    def change_time(self, new_time: datetime.datetime) -> None:
        """
        Sets the RTC to a new date and time.

        Args:
            new_time (datetime.datetime): The new date and time to set.
        Raises:
            RuntimeError: If an error occurs while changing the time.
        """
        try:
            self.rtc.datetime = new_time.timetuple()
        except Exception as e:
            raise RuntimeError(f"Error while changing time: {e}")

    def get_time(self) -> datetime.datetime:
        """
        Retrieves the current date and time from the RTC.

        Returns:
            datetime.datetime: The current date and time.
        Raises:
            RuntimeError: If an error occurs while getting the time.
        """
        try:
            rtc_datetime = time.mktime(self.rtc.datetime)
            return datetime.datetime.fromtimestamp(rtc_datetime)
        except Exception as e:
            raise RuntimeError(f"Error while getting time: {e}")
