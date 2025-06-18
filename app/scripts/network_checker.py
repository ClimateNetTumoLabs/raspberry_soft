import socket
import subprocess
import time
from logger_config import logging


def check_network() -> bool:
    """
    Checks if a network connection with internet access is established using multiple methods.

    Returns:
        bool: True if internet connectivity is available, False otherwise.
    """
    # Method 1: Try to connect to a reliable DNS server
    try:
        # Connect to Google's DNS with a short timeout
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        logging.info("Internet connection verified via socket connection")
        return True
    except (socket.timeout, socket.error, OSError):
        logging.error("Socket connection test failed")
        # Continue to next method

    # Method 2: Try ping to a reliable host
    try:
        ping_cmd = "ping -c 1 -W 2 8.8.8.8"
        result = subprocess.run(ping_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            logging.info("Internet connection verified via ping")
            return True
        else:
            logging.error("Ping test failed")
    except Exception as e:
        logging.error(f"Error during ping test: {str(e)}")

    # Method 3: Try to connect to the MQTT broker endpoint (if available)
    try:
        from config import MQTT_BROKER_ENDPOINT
        if MQTT_BROKER_ENDPOINT:
            # Try to resolve the hostname
            socket.gethostbyname(MQTT_BROKER_ENDPOINT)
            logging.info(f"Internet connection verified via DNS resolution of {MQTT_BROKER_ENDPOINT}")
            return True
    except (socket.gaierror, ImportError, Exception) as e:
        logging.error(f"MQTT broker connection test failed: {str(e)}")

    logging.error("All network connectivity tests failed - no internet connection available")
    return False


def get_network_interface() -> str:
    """
    Retrieves the network interface currently used for the default route.
    This function is kept for backward compatibility but is no longer used
    for determining connectivity.

    Returns:
        str: The name of the network interface, or False if not found.
    """
    try:
        result = subprocess.run("route | grep '^default' | grep -o '[^ ]*$'",
                                shell=True, capture_output=True, text=True)
        output = result.stdout.strip()
        lines = output.split('\n')
        return lines[0] if lines and lines[0] else False
    except Exception as e:
        logging.error(f"Error getting network interface: {str(e)}")
        return False
