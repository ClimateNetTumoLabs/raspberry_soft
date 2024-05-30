import socket
import subprocess
import time
from datetime import datetime

import ntplib
import pytz
from logger_config import logging

from .network_checker import check_network
from .rtc import RTCControl


def update_rtc_time():
    """
    Updates the system's real-time clock (RTC) time using Network Time Protocol (NTP) time.

    Attempts to synchronize the RTC time with the NTP server time. Tries up to three times to establish a network
    connection and retrieve the NTP time. If successful, updates the RTC time and returns True. If unsuccessful,
    logs the error and returns False.

    Returns:
        bool: True if RTC time was successfully updated, False otherwise.
    """
    for i in range(3):
        if check_network():
            tz = pytz.timezone('Asia/Yerevan')
            ntp_server = 'pool.ntp.org'
            ntp_client = ntplib.NTPClient()
            try:
                response = ntp_client.request(ntp_server)
                ntp_time = response.tx_time

                try:
                    rtc = RTCControl()
                    rtc.change_time(datetime.utcfromtimestamp(ntp_time).replace(tzinfo=pytz.utc).astimezone(tz=tz))
                    return True
                except Exception as e:
                    logging.error(f"Failed to change RTC time: {e}")
                    return False
            except Exception:
                return False

        time.sleep(5)

    return False


def update_time():
    """
    Updates the system's time using Network Time Protocol (NTP) time or RTC time if NTP is unavailable.

    Attempts to synchronize the system time with the NTP server time. If successful, updates the system time
    and the RTC time. If NTP synchronization fails, attempts to update the system time using the RTC time.
    Logs any errors encountered during the process.

    Returns:
        bool: True if system time was successfully updated, False otherwise.
    """
    for i in range(3):
        if check_network():
            tz = pytz.timezone('Asia/Yerevan')
            ntp_server = 'pool.ntp.org'
            ntp_client = ntplib.NTPClient()
            try:
                response = ntp_client.request(ntp_server)
                ntp_time = response.tx_time
                new_datetime = datetime.utcfromtimestamp(ntp_time).replace(tzinfo=pytz.utc).astimezone(tz=tz).strftime(
                    '%Y-%m-%d %H:%M:%S')
                subprocess.call(['sudo', 'date', '-s', new_datetime])
                logging.info(f'Updated time from NTP server: {new_datetime}')
                try:
                    rtc = RTCControl()
                    rtc.change_time(datetime.utcfromtimestamp(ntp_time).replace(tzinfo=pytz.utc).astimezone(tz=tz))
                except Exception as e:
                    logging.error(f"Failed to change RTC time: {e}")
                return True
            except socket.gaierror:
                logging.error("Failed to get time from NTP")
            except Exception as e:
                logging.error(f"Error occurred during getting time from NTP: {e}")

        else:
            logging.error("Failed to establish network connection for changing time")

        time.sleep(5)

    rtc = RTCControl()
    rtc_time = rtc.get_time()

    if rtc_time:
        try:
            new_time = rtc_time.strftime('%Y-%m-%d %H:%M:%S')

            subprocess.call(['sudo', 'date', '-s', new_time])
            logging.info(f'Updated time from RTC: {new_time}')
            return True
        except Exception as e:
            logging.error(f"Error occurred during updating time from RTC: {e}")
    else:
        logging.error("Failed to get time from RTC")

    return False
