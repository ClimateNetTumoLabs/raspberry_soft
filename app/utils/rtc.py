import datetime
import time
import adafruit_ds3231
import board


class RTCControl:
    def __init__(self) -> None:
        """
        Initializes the RTCControl instance.
        """
        try:
            self.i2c = board.I2C()
            self.rtc = adafruit_ds3231.DS3231(self.i2c)
            # Test communication
            _ = self.rtc.datetime
        except Exception as e:
            raise RuntimeError(f"RTC initialization failed: {e}")

    def change_time(self, new_time: datetime.datetime) -> None:
        try:
            # Ensure we're working with naive datetime (no timezone)
            if new_time.tzinfo is not None:
                new_time = new_time.astimezone(datetime.timezone.utc).replace(tzinfo=None)

            # Create time tuple explicitly
            rtc_time = time.struct_time((
                new_time.year,
                new_time.month,
                new_time.day,
                new_time.hour,
                new_time.minute,
                new_time.second,
                new_time.weekday(),
                -1,  # -1 for day of year
                -1  # -1 for DST
            ))
            self.rtc.datetime = rtc_time
            print(f"RTC set to: {new_time}")
        except Exception as e:
            raise RuntimeError(f"Error while changing time: {e}")

    def get_time(self) -> datetime.datetime:
        try:
            rtc_struct = self.rtc.datetime
            # Convert struct_time to datetime
            return datetime.datetime(
                year=rtc_struct.tm_year,
                month=rtc_struct.tm_mon,
                day=rtc_struct.tm_mday,
                hour=rtc_struct.tm_hour,
                minute=rtc_struct.tm_min,
                second=rtc_struct.tm_sec
            )
        except Exception as e:
            raise RuntimeError(f"Error while getting time: {e}")

    def sync_from_system(self) -> None:
        """Sync RTC from system time"""
        system_time = datetime.datetime.now()
        self.change_time(system_time)
        print(f"RTC synced from system time: {system_time}")
