#!/bin/sh

# Git clone and check if the clone was successful
git clone https://github.com/ApinHovo/dpsohvuifdhvbiusdhisd.git
if [ $? -eq 0 ]; then
    echo "Repository was succesfully cloned"
else
    echo "Error while cloning the repository"
    exit 1  # Exit the script with an error
fi

username="raspberry"
script_dir="/home/$username/scripts/"
service_dir="/etc/systemd/system/"
inet_files=0

# Change directory to dpsohvuifdhvbiusdhisd
cd dpsohvuifdhvbiusdhisd

# Check if AutoUpdateUpgrade.service already exists in service_dir
if [ ! -f "$service_dir/AutoUpdateUpgrade.service" ]; then
    # Move AutoUpdateUpgrade.service to service_dir if it does not exist there
    sed -i "s/username/$username/g" AutoUpdateUpgrade.service
    mv AutoUpdateUpgrade.service "$service_dir"
    sudo systemctl daemon-reload
    sudo systemctl enable AutoUpdateUpgrade.service
    sudo systemctl start AutoUpdateUpgrade.service
else
    echo "The file AutoUpdateUpgrade.service already exists in $service_dir."
fi

# Check if InetCheckConnect.service already exists in service_dir
if [ ! -f "$service_dir/InetCheckConnect.service" ]; then
    # Check if the script_dir exists and create if it doesn't
    if [ ! -d "$script_dir" ]; then
        mkdir -p "$script_dir"
    fi
    mv InetCheckConnect.py "$script_dir"

    # Move InetCheckConnect.py to script_dir if inet_files is 0
    if [ "$inet_files" -eq 0 ]; then
        sed -i "s/username/$username/g" InetCheckConnect.service
        mv InetCheckConnect.service "$service_dir"
        sudo systemctl start NetworkManager
        sudo systemctl enable NetworkManager
        sudo systemctl daemon-reload
        sudo systemctl enable InetCheckConnect.service
        sudo systemctl start InetCheckConnect.service
    else
        echo "The file InetCheckConnect.py already exists in $script_dir."
    fi

else
    echo "The file InetCheckConnect.service already exists in $service_dir."
fi

cd ../

# Remove the cloned directory dpsohvuifdhvbiusdhisd
rm -rf dpsohvuifdhvbiusdhisd
if [ $? -eq 0 ]; then
    echo "The dpsohvuifdhvbiusdhisd was successfully removed"
else
    echo "Error while removing the dpsohvuifdhvbiusdhisd directory"
    exit 1  # Exit the script with an error
fi

echo "OK"
