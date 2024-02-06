#!/bin/bash

# Enable interfaces
sudo raspi-config nonint do_ssh 0
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial 0

# Install vim
sudo apt update
sudo apt install -y vim

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create PostgreSQL database and change password
sudo -u postgres createdb raspi_data
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'climatenet2024';"

# Configure git editor
git config --global core.editor "vim"

# Copy service files
cp raspberry_soft/ServiceFiles/InetCheckConnect/InetCheckConnect.service /etc/systemd/system/
mkdir -p "/home/raspberry/scripts/"
mv raspberry_soft/ServiceFiles/InetCheckConnect/InetCheckConnect.py /home/raspberry/scripts/

cp raspberry_soft/ServiceFiles/ProgramAutoRun/ProgramAutoRun.service /etc/systemd/system/

# Reload systemd to recognize new service files
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager

sudo systemctl enable InetCheckConnect
sudo systemctl enable ProgramAutoRun
sudo systemctl start InetCheckConnect
sudo systemctl start ProgramAutoRun

echo "Installation completed successfully."