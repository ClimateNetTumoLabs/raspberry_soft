#!/bin/bash

# Enable interfaces
sudo raspi-config nonint do_ssh 0
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0

# Configure git editor
git config --global core.editor "vim"

# Copy service files
cp ServiceFiles/InternetCheckConnect/InetCheckConnect.service /etc/systemd/system/
mkdir -p "/home/raspberry/scripts/"
cp ServiceFiles/InternetCheckConnect/inet_check_connect.py /home/raspberry/scripts/

cp ServiceFiles/ProgramAutoRun/ProgramAutoRun.service /etc/systemd/system/


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

sudo systemctl enable InetCheckConnect
sudo systemctl start InetCheckConnect

echo "Installation completed successfully."