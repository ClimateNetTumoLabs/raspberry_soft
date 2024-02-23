"""
    Script for updating the system time from an NTP server.

    This script provides a function, update_time_from_ntp, for continuously updating the system time from an NTP server.

    Function Docstring:
    --------------------
    update_time_from_ntp():
        Continuously updates the system time from an NTP server. Uses the 'Asia/Yerevan' timezone.

    Module Usage:
    -------------
    To use this script, call the update_time_from_ntp() function.
"""

import pytz
import ntplib
import subprocess
import socket
import time
from datetime import datetime
from logger_config import *
from .network_checker import check_network
from .rtc import RTCControl


def update_time():
    """
    Updates the system time from an NTP server. Uses the 'Asia/Yerevan' timezone.
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
                logging.error(f"Failed to get time from NTP")
            except Exception as e:
                logging.error(f"Error occurred during getting time from NTP: {e}")

        else:
            logging.error(f"Failed to establish network connection for changing time")

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