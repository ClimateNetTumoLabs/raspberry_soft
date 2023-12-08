"""
    Script for changing the mode of the /dev/ttyS0 device.

    This script provides a function, chmod_tty, for changing the mode of the /dev/ttyS0 device to 777.

    Function Docstring:
    --------------------
    chmod_tty():
        Changes the mode of /dev/ttyS0 to 777.

    Module Usage:
    -------------
    To use this script, call the chmod_tty() function.
"""

import subprocess
from logger_config import *


def chmod_tty():
    """
    Changes the mode of /dev/ttyS0 to 777.
    """
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
