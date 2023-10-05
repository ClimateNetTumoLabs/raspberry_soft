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
    if is_connected():
        return True
    else:
        logging.error("Failed to establish network connection.")
        return False