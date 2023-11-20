import subprocess
import pytz
import ntplib
import socket
import sys
import math
import time
from datetime import datetime
from logger_config import *
from network_check import check_network

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


def get_quantity(data_lst):
    size_in_bytes = sys.getsizeof(data_lst)
    size = 256 * 1024 * 1024

    return math.ceil(size_in_bytes / size)


def split_data(data_lst):
    quantity = get_quantity(data_lst)
    avg = len(data_lst) // quantity
    remainder = len(data_lst) % quantity
    
    result = []
    start = 0
    for i in range(quantity):
        if i < remainder:
            end = start + avg + 1
        else:
            end = start + avg
        result.append(data_lst[start:end])
        start = end

    return result


def chmod_tty():
    command = 'sudo chmod 777 /dev/ttyS0'

    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logging.info(f"Successfully changed mode for /dev/ttyS0")
        else:
            logging.error(f"Error while changing mode for /dev/ttyS0: {result.stderr}")
    except Exception as e:
        logging.error(f"Error while changing mode for /dev/ttyS0 {str(e)}")
        raise
