import socket
import subprocess
import time


def check_internet(host="8.8.8.8", port=53, timeout=5):
    """Check if the internet connection is available."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def reconnect(ssid="MyWiFi", password="mypassword"):
    """Try to reconnect to the internet via LAN or Wi-Fi."""
    print("[Network] Checking connection...")

    if check_internet():
        print("[Network] Internet is already connected.")
        return True

    print("[Network] No internet connection. Trying to reconnect...")

    # Try to reconnect to Ethernet (LAN)
    print("[Network] Trying Ethernet...")
    try:
        subprocess.run(["sudo", "dhclient", "-r"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "dhclient", "eth0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
        if check_internet():
            print("[Network] Ethernet reconnected successfully.")
            return True
    except Exception as e:
        print(f"[Network] Ethernet reconnect failed: {e}")

    # Try to reconnect to Wi-Fi
    print(f"[Network] Trying Wi-Fi SSID '{ssid}'...")
    try:
        # Disconnect current Wi-Fi (if any)
        subprocess.run(["sudo", "nmcli", "device", "disconnect", "wlan0"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        # Reconnect to Wi-Fi
        subprocess.run(["sudo", "nmcli", "device", "wifi", "connect", ssid, "password", password], check=False)
        time.sleep(5)
        if check_internet():
            print("[Network] Wi-Fi reconnected successfully.")
            return True
    except Exception as e:
        print(f"[Network] Wi-Fi reconnect failed: {e}")

    print("[Network] Reconnection failed. Check your cables or Wi-Fi credentials.")
    return False


# Example usage
if __name__ == "__main__":
    if check_internet():
        print("Internet is connected.")
    else:
        print("Internet is not connected. Attempting to reconnect...")
        reconnect(ssid="YourSSID", password="YourPassword")
