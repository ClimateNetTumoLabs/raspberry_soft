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
            logging.info(f"RTC synced with system time: {system_time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            raise RuntimeError(f"Error while syncing RTC from system: {e}")

    def sync_from_ntp(self) -> bool:
        """
        Synchronizes system time with NTP and updates RTC.

        Returns:
            bool: True if synchronization was successful, False otherwise.
        """
        try:
            # First, try to sync system time with NTP
            logging.info("Attempting to sync system time with NTP...")
            result = subprocess.run(
                ["sudo", "timedatectl", "set-ntp", "true"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                logging.warning("Failed to enable NTP sync via timedatectl")
                return False

            # Wait a moment for NTP to sync
            time.sleep(2)

            # Now sync RTC with system time
            self.sync_from_system()
            logging.info("Successfully synced RTC with NTP time")
            return True

        except subprocess.TimeoutExpired:
            logging.warning("NTP sync timed out")
            return False
        except Exception as e:
            logging.error(f"Error during NTP sync: {e}")
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
            # First check if we have internet and can get NTP time
            if check_internet():
                try:
                    # Try to get system time (which should be NTP-synced if configured)
                    system_time = datetime.datetime.now()

                    # Validate that system time is reasonable (not default/epoch)
                    # Raspberry Pi without RTC might have a default date if not synced
                    if system_time.year > 2020:  # Reasonable check for recent time
                        logging.info("Using internet-synced system time")
                        return system_time
                    else:
                        logging.warning(f"System time appears invalid: {system_time}")
                except Exception as e:
                    logging.warning(f"Failed to get system time: {e}")

            # If no internet or system time invalid, fall back to RTC
            logging.info("Using RTC hardware time (no internet or invalid system time)")
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