# Internet Connection Check/Connect Service

This systemd service file, along with the provided Python script, is designed to continuously check for an internet connection and attempt to connect to a known Wi-Fi network if no connection is available. The service will run at system startup and will restart every 60 seconds (configurable) to ensure continuous monitoring of the internet connection.


## Installation and Usage

1. Save the provided Python script (`InetCheckConnect.py`) to the directory `/home/username/scripts` (replace username with the actual `username` of the user).

2. Open a text editor as the root user (e.g., using `sudo vim /etc/systemd/system/InetCheckConnect.service`).

3. Copy and paste the `InetCheckConnect.service` file contents into the text editor.

4. Modify the `ExecStart` and `WorkingDirectory` directive to replace username with the actual `username` of the user.

5. Save the file and exit the text editor.

6. For connecting to Wi-Fi we also need to start NetworkManager

   ```
   sudo systemctl start NetworkManager
   ```

   Enable restarting the network manager when the system reboots

   ```
   sudo systemctl enable NetworkManager
   ```

7. Reload the systemd daemon to recognize the new unit:

   ```
   sudo systemctl daemon-reload
   ```
   Enable the service to start on boot:

   ```
   sudo systemctl enable InetCheckConnect.service
   ```

   Start the service

   ```
   sudo systemctl start InetCheckConnect.service
   ```

The system will now execute the InetCheckConnect.py script continuously, checking for an internet connection and attempting to connect to a known Wi-Fi network when required. The output of the script will be logged to the `internet.log` file on the user's desktop.
