import subprocess

from logger_config import logging


def get_network_interface() -> str:
    """
    Retrieves the network interface currently used for the default route.

    Returns:
        str: Name of the network interface, or False if no interface is found.
    """
    result = subprocess.run("route | grep '^default' | grep -o '[^ ]*$'", shell=True, capture_output=True, text=True)
    output = result.stdout
    lines = output.split('\n')

    return lines[0] if lines[0] else False


def check_network() -> bool:
    """
    Checks if a network connection is established by verifying the presence of a network interface.

    Returns:
        bool: True if a network connection is established, False otherwise.
    """
    interface = get_network_interface()

    if interface:
        return True
    else:
        logging.error("Failed to establish network connection.")
        return False
