import pytz
import ntplib
import subprocess
import socket
import time
from datetime import datetime
from logger_config import *
from .network_checker import check_network


def update_time_from_ntp():
    while True:
        if check_network():
            tz = pytz.timezone('Asia/Yerevan')
            ntp_server = 'pool.ntp.org'
            ntp_client = ntplib.NTPClient()
            try:
                response = ntp_client.request(ntp_server)
                ntp_time = response.tx_time
                new_datetime = datetime.utcfromtimestamp(ntp_time).replace(tzinfo=pytz.utc).astimezone(tz=tz).strftime('%Y-%m-%d %H:%M:%S')
                subprocess.call(['sudo', 'date', '-s', new_datetime])
                logging.info(f'Updated time from NTP server: {new_datetime}')
                return True
            except socket.gaierror:
                logging.error(f"Failed to get time from NTP")
            except Exception as e:
                logging.error(f"Error occurred during getting time from NTP: {e}")
            
        else:
            logging.error(f"Failed to establish network connection for changing time")

        time.sleep(5)