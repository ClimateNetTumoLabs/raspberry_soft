"""
    Utility script for checking the availability of a network connection.

    This script provides two functions:
    - get_network_interface() -> str: Retrieves the name of the network interface currently used for the default route.
    - check_network() -> bool: Checks the availability of a network connection.

    Function Signatures:
    ---------------------
    get_network_interface() -> str:
        Retrieves the name of the network interface currently used for the default route.

    check_network() -> bool:
        Checks the availability of a network connection.

    Module Usage:
    -------------
    To use this script, call the check_network() function to determine the availability of a network connection.
    If the function returns True, a network connection is available; otherwise, an error is logged, and False is returned.
"""

import subprocess
from logger_config import *


def get_network_interface() -> str:
    """
    Retrieves the name of the network interface currently used for the default route.

    Returns:
        str: The name of the network interface.
    """
    result = subprocess.run("route | grep '^default' | grep -o '[^ ]*$'", shell=True, capture_output=True, text=True)
    output = result.stdout
    lines = output.split('\n')

    return lines[0] if lines[0] else False


def check_network() -> bool:
    """
    Checks the availability of a network connection.

    Returns:
        bool: True if a network connection is available, False otherwise.
    """
    interface = get_network_interface()

    if interface:
        return True
    else:
        logging.error("Failed to establish network connection.")
        return False
