import datetime
import time
import subprocess
from .network import check_internet
from logger_config import logging
import adafruit_ds3231
import board


class RTCControl:
    """
    Controls a DS3231 Real-Time Clock (RTC) module with internet-aware time retrieval.

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

    def sync_from_system(self) -> None:
        """
        Synchronizes the RTC with the system time (Raspberry Pi time).

        Raises:
            RuntimeError: If an error occurs while syncing time.
        """
        try:
            system_time = datetime.datetime.now()
            self.change_time(system_time)
        except Exception as e:
            raise RuntimeError(f"Error while syncing RTC from system: {e}")

    def sync_system_from_rtc(self) -> None:
        """
        Sets system time from RTC hardware.
        Requires root privileges.
        """
        try:
            rtc_time = self.get_rtc_time()
            formatted = rtc_time.strftime("%Y-%m-%d %H:%M:%S")

            subprocess.run(
                ["sudo", "date", "-s", formatted],
                check=True
            )

            logging.info(f"System synced from RTC: {formatted}")

        except Exception as e:
            raise RuntimeError(f"Failed to sync system time from RTC: {e}")

    def sync_from_ntp(self) -> bool:
        """
        Synchronizes system time with NTP and updates RTC.

        Returns:
            bool: True if synchronization was successful, False otherwise.
        """
        try:
            result = subprocess.run(
                ["sudo", "timedatectl", "set-ntp", "true"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return False

            time.sleep(2)
            self.sync_from_system()
            logging.info("Time synced: NTP → System → RTC")
            return True

        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            logging.error(f"NTP sync error: {e}")
            return False

    def get_time(self) -> datetime.datetime:
        """
        Retrieves the current date and time.

        Priority: Internet NTP > System time > RTC hardware

        Returns:
            datetime.datetime: The current date and time.
        Raises:
            RuntimeError: If an error occurs while getting time from all sources.
        """
        try:
            if check_internet():
                system_time = datetime.datetime.now()
                if system_time.year > 2020:
                    return system_time

            rtc_datetime = time.mktime(self.rtc.datetime)
            return datetime.datetime.fromtimestamp(rtc_datetime)

        except Exception as e:
            raise RuntimeError(f"Error while getting time from all sources: {e}")

    def get_rtc_time(self) -> datetime.datetime:
        """
        Retrieves the current date and time directly from RTC hardware only.

        Returns:
            datetime.datetime: The current date and time from RTC.
        Raises:
            RuntimeError: If an error occurs while getting time from RTC.
        """
        try:
            rtc_datetime = time.mktime(self.rtc.datetime)
            return datetime.datetime.fromtimestamp(rtc_datetime)
        except Exception as e:
            raise RuntimeError(f"Error while getting time from RTC: {e}")