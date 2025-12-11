import socket
import subprocess
import time
from logger_config import logging
from config import SSID, PASSWORD

def check_internet(host="8.8.8.8", port=53, timeout=5):
    """Check if the internet connection is available."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def reconnect(ssid=SSID, password=PASSWORD):
    """Try to reconnect to the internet via LAN or Wi-Fi."""
    logging.info("[Network] Checking connection...")

    if check_internet():
        logging.info("[Network] Internet is already connected.")
        return True

    logging.info("[Network] No internet connection. Trying to reconnect...")

    logging.info(f"[Network] Trying Wi-Fi SSID '{ssid}'...")
    try:
        # Disconnect current Wi-Fi (if any)
        subprocess.run(["sudo", "nmcli", "device", "disconnect", "wlan0"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        # Reconnect to Wi-Fi
        subprocess.run(["sudo", "nmcli", "device", "wifi", "connect", ssid, "password", password], check=False)
        if check_internet():
            logging.info("[Network] Wi-Fi reconnected successfully.")
            return True
    except Exception as e:
        logging.info(f"[Network] Wi-Fi reconnect failed: {e}")

    # Try to reconnect to Ethernet (LAN)
    logging.info("[Network] Trying Ethernet...")
    try:
        subprocess.run(["sudo", "dhclient", "-r"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "dhclient", "eth0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if check_internet():
            logging.info("[Network] Ethernet reconnected successfully.")
            return True
    except Exception as e:
        logging.info(f"[Network] Ethernet reconnect failed: {e}")

    logging.info("[Network] Reconnection failed. Check your cables or Wi-Fi credentials.")
    return False
