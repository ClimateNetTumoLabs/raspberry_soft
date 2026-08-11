#!/bin/bash
set -e

# Where this checkout actually lives, and who owns it. The service files ship with
# /home/raspberry paths as their default, but nothing requires that name: the units
# are rewritten with these values as they are copied into /etc/systemd/system, which
# git does not track, so ServiceFiles/ stays clean and git pull never conflicts.
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
STATION_USER="${STATION_USER:-$(stat -c '%U' "$REPO_DIR")}"
echo "Installing for user '${STATION_USER}' from ${REPO_DIR}"

# None of these ship with Raspberry Pi OS Lite, and all are no-ops on an
# already-provisioned station:
#   swig, liblgpio-dev - build lgpio, which has no prebuilt wheel for 64-bit/Python 3.13
#   python3-dev        - Python.h, needed by lgpio, rpi-ws281x, RPi.GPIO and sysv-ipc
#   python3-venv       - the venv step below
sudo apt install -y swig liblgpio-dev python3-dev python3-venv

# Enable interfaces
sudo raspi-config nonint do_ssh 0
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial_cons 1
sudo raspi-config nonint do_serial_hw 0

# Configure git editor
git config --global core.editor "vim"

echo "dtoverlay=pi3-miniuart-bt" | sudo tee -a /boot/firmware/config.txt
echo "dtoverlay=pi3-miniuart-bt" | sudo tee -a /boot/config.txt

# Copy the units, substituting this station's user and checkout path. The two
# expressions are deliberately narrow: a blanket s/raspberry/$STATION_USER/ would
# also rewrite "raspberry_soft" in every path.
for unit in WifiMonitor.service ProgramAutoRun.service; do
    sed -e "s|/home/raspberry/workspace/raspberry_soft|${REPO_DIR}|g" \
        -e "s|^User=raspberry$|User=${STATION_USER}|" \
        -e "s|^Group=raspberry$|Group=${STATION_USER}|" \
        "$REPO_DIR/ServiceFiles/$unit" | sudo tee "/etc/systemd/system/$unit" >/dev/null
done

sudo chmod +x "$REPO_DIR/ServiceFiles/wifi_monitor.sh"

python3 -m venv app/venv
source app/venv/bin/activate

# Install Python dependencies
pip install -r app/requirements.txt

# Deactivate virtual environment
deactivate

# Reload systemd to recognize new service files
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager

sudo systemctl enable WifiMonitor.service
sudo systemctl start WifiMonitor.service

sudo systemctl enable ProgramAutoRun.service
sudo systemctl start ProgramAutoRun.service

echo "Installation completed successfully."
