#!/bin/bash
# Change the path if doesn't correspond to yours
CONFIG_FILE="/home/raspberry/workspace/raspberry_soft/app/config.py"

# Extract SSID and PASSWORD from config.py
WIFI_SSID=$(grep '^SSID = ' "$CONFIG_FILE" | sed 's/SSID = "\(.*\)"/\1/')
WIFI_PASSWORD=$(grep '^PASSWORD = ' "$CONFIG_FILE" | sed 's/PASSWORD = "\(.*\)"/\1/')

# Check if credentials were found
if [ -z "$WIFI_SSID" ] || [ -z "$WIFI_PASSWORD" ]; then
    echo "$(date): Error - Could not read WiFi credentials from $CONFIG_FILE"
    exit 1
fi

# Function to check internet connectivity
check_internet() {
    timeout 5 bash -c "cat < /dev/null > /dev/tcp/8.8.8.8/53" 2>/dev/null
    return $?
}

# If already connected, exit successfully
if check_internet; then
    echo "Already connected to wifi $WIFI_SSID"
    exit 0
fi

# Disconnect current WiFi
nmcli device disconnect wlan0 2>/dev/null

# Connect to WiFi
if nmcli device wifi connect "$WIFI_SSID" password "$WIFI_PASSWORD" 2>&1 | grep -q "successfully"; then
    echo "$(date): Connected to $WIFI_SSID"
    exit 0
else
    echo "$(date): Failed to connect to $WIFI_SSID"
    exit 1
fi
