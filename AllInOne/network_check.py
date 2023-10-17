import subprocess
import logging
from logger_config import *


def get_network_interface():
    """
    Retrieve the network interface name associated with the default route.

    This function runs a subprocess command to obtain the network interface name
    associated with the default route. It is used to check for an active network
    connection.

    Returns:
        str: The name of the network interface if a default route is found.
        False: If no network interface is associated with the default route.

    Example:
        >>> interface_name = get_network_interface()
    """
    result = subprocess.run("route | grep '^default' | grep -o '[^ ]*$'", shell=True, capture_output=True, text=True)
    output = result.stdout
    lines = output.split('\n')
    
    return lines[0] if lines[0] else False


def check_network():
    """
    Check the availability of a network connection.

    This function checks whether there is an active network connection by
    calling the 'get_network_interface' function.

    Returns:
        bool: True if a network connection is available, False otherwise.

    Example:
        >>> if check_network():
        >>>     print("Network connection is established.")
        >>> else:
        >>>     print("Failed to establish network connection.")
    """
    interface = get_network_interface()

    if interface:
        return True
    else:
        logging.error("Failed to establish network connection.")
        return False
