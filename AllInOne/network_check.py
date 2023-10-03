import subprocess
import time
import logging
from logger_config import *


def get_network_interface():
    result = subprocess.run("route | grep '^default' | grep -o '[^ ]*$'", shell=True, capture_output=True, text=True)
    output = result.stdout
    
    lines = output.split('\n')
    
    return lines[0] if lines[0] else False


def is_connected():
    interface = get_network_interface()

    if interface:
        return True
    else:
        return False


def check_network():
    retry_delay = 30
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        if is_connected():
            logging.info("Connected to Network")
            return True
        else:
            return False
            logging.warning("Network connection lost. Retrying in {} seconds...".format(retry_delay))
            time.sleep(retry_delay)
            retry_count += 1

    if retry_count == max_retries:
        logging.error("Failed to establish network connection after {} retries.".format(max_retries))
        return False