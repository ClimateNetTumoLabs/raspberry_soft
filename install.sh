#!/bin/bash

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

# Copy service files
cp ServiceFiles/WifiMonitor.service /etc/systemd/system/
cp ServiceFiles/ProgramAutoRun.service /etc/systemd/system/

sudo chmod +x /home/raspberry/workspace/raspberry_soft/ServiceFiles/wifi_monitor.sh

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
